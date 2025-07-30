"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import logging
import os
import re
import platform
import json
import glob
import shutil
import tempfile
import zipfile
import tqdm
import time
from blackduck_c_cpp.util import util
from blackduck_c_cpp.util.zip_file import MyZipFile
from blackduck_c_cpp.util import global_settings
import uuid
import copy

class SigScanner:

    def __init__(self, cov_base_path, hub_api, files_notdetect_from_pkgmgr, project_name, project_version_name,
                 code_location_name, cov_emit_output_sig, blackduck_output_dir, offline_mode, scan_cli_dir,
                 use_offline_files, os_dist, additional_sig_scan_args, expand_sig_files, scan_interval,
                 json_splitter_limit, bdio_split_max_file_entries, bdio_split_max_chunk_nodes,
                 disable_bdio_json_splitter, skip_includes, port, verbose):
        self.hub_api = hub_api
        self.hub = self.hub_api.hub
        self.hub_version = self.hub_api.get_hub_version()
        self.major, self.minor, self.patch = self.hub_version.split('.')
        self.sleep_interval = scan_interval  # time to wait between scans
        self.project_name = project_name
        self.project_version_name = project_version_name
        self.code_location_name = code_location_name + '-SIG'
        self.insecure = hub_api.insecure
        self.additional_sig_scan_args = additional_sig_scan_args
        self.expand_sig_files = expand_sig_files
        self.offline_mode = offline_mode
        self.use_offline_files = use_offline_files

        if self.additional_sig_scan_args:
            self.expand_sig_files = True if global_settings.snippet_match in self.additional_sig_scan_args.lower() else self.expand_sig_files
        self.version_grt = ((int(self.major) >= 2021 and int(self.minor) >= 10) or int(self.major) >= 2022)
        # as --bdio2 splitter doesn't work with archives
        if (self.version_grt and self.offline_mode) or (self.use_offline_files and self.version_grt):
            self.expand_sig_files = True
        self.json_splitter_limit = json_splitter_limit
        self.bdio_split_max_file_entries = bdio_split_max_file_entries
        self.bdio_split_max_chunk_nodes = bdio_split_max_chunk_nodes
        self.disable_bdio_json_splitter = disable_bdio_json_splitter
        self.skip_includes = skip_includes
        self.cov_emit_output_sig = cov_emit_output_sig
        self.os_dist = os_dist
        self.api_token = hub_api.api_token
        self.cov_base_path = cov_base_path
        self.blackduck_output_dir = blackduck_output_dir
        self.sig_scan_output_directory = os.path.join(blackduck_output_dir, 'sig_scan')
        self.sig_files_output_path = os.path.join(self.sig_scan_output_directory, 'sig_files')
        self.sig_scan_zip_output_directory = os.path.join(self.sig_scan_output_directory, 'zip_file')
        self.zip_output_path = os.path.join(self.sig_scan_zip_output_directory, 'sig_scan.zip')
        self.scan_cli_home = scan_cli_dir
        self.files_notdetect_from_pkgmgr = files_notdetect_from_pkgmgr
        self.files_to_zip = None
        self.scan_cli_directory = None
        self.scan_cli_path = None
        self.cov_header_files = {}
        self.sig_scanner_found = False
        self.json_file = self.bdio_file = None
        self.upload_dry_run = self.use_offline_files
        self.proxy_settings = ''
        self.url_split = "://"
        self.op_sys = platform.system()
        self.port = port
        self.verbose = verbose

    def get_files_to_zip(self):
        """ collect all files to send to signature scanner"""
        if self.skip_includes:
            self.cov_emit_output_sig = [emit_file for emit_file in self.cov_emit_output_sig if not (
                    re.match(global_settings.hpp_pattern, emit_file.strip()) or
                    re.match(global_settings.hxx_pattern, emit_file.strip()) or
                    re.match(global_settings.h_pattern, emit_file.strip()))]
        self.files_to_zip = set(self.cov_emit_output_sig)
        if self.files_notdetect_from_pkgmgr:
            [[[self.files_to_zip.add(path) for path in paths if os.path.exists(path)] for paths in type.values()] for
             type in
             self.files_notdetect_from_pkgmgr.values()]

    def copy_files_to_dir(self):
        """
        write files to scan to exploded directory
        """
        self.get_files_to_zip()
        if not os.path.exists(self.sig_scan_output_directory):
            os.makedirs(self.sig_scan_output_directory)

        logging.info("The signature files to scan will be written to {}".format(self.sig_files_output_path))
        logging.info("Collecting files returned by cov-emit...")
        logging.info("Number of files in sig_files directory are {}".format(len(self.files_to_zip)))

        if os.path.exists(self.sig_files_output_path):
            shutil.rmtree(self.sig_files_output_path)
        files_count = 0
        for each_file in tqdm.tqdm(self.files_to_zip, total=len(self.files_to_zip)):
            dest_filepath = ''
            try:
                # exclude coverity configuration header files that are in the emit directory
                if os.path.join(self.blackduck_output_dir, 'emit') in each_file:
                    continue
                # split drive -> drive is mount point and path is in tail
                file_spath = os.path.splitdrive(each_file)[1]
                dest_filepath = self.sig_files_output_path + file_spath
                dest_folder = os.path.dirname(dest_filepath)

                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                shutil.copy(each_file, dest_filepath)
                files_count += 1
            except IsADirectoryError:
                continue
            except PermissionError:
                continue
            except Exception as e:
                if len(dest_filepath) > 260 and self.op_sys == 'Windows':
                    logging.warning(
                        "You are using Windows and the file path exceeds the default limit of 260 characters. Check the character limit on your system and consider removing the limit to include this file in the scan. The rest of the scan will proceed.")
                    logging.warning("Not copying file to location: {}".format(dest_filepath))
                else:
                    logging.warning("Exception is {}".format(e))
                continue
        logging.debug("Number of files added in sig_files directory are {}".format(files_count))

    def zip_files(self):
        """
        compress the files from run_cov_emit and from files_notdetect_from_pkgmgr into a zip archive
        os.path.exists() check done in emit_wrapper.py
        """
        self.get_files_to_zip()
        if not os.path.exists(self.sig_scan_zip_output_directory):
            os.makedirs(self.sig_scan_zip_output_directory)
        logging.info("The signature zip file to scan will be written to {}".format(self.zip_output_path))
        logging.info("Zipping files returned by cov-emit...")
        logging.info("Number of files in sig zip file is {}".format(len(self.files_to_zip)))
        util.zip_files(self.files_to_zip, self.zip_output_path)

    def get_sig_scanner_download_url(self):
        """
        construct the URL from which to download the signature scanner from Black Duck
        """
        sig_scanner_url = self.hub_api.bd_url + '/download/scan.cli'
        if self.op_sys == 'Windows':
            sig_scanner_url += '-windows'
        if self.op_sys == 'Darwin':
            sig_scanner_url += '-macosx'
        sig_scanner_url += '.zip'
        return sig_scanner_url

    def find_any_sig_scanner(self):
        """
        check if the sig scanner for any black duck version is already on the system
        """
        try:
            self.scan_cli_directory = os.path.basename(
                sorted(glob.glob(os.path.join(self.scan_cli_home, 'scan.cli-*')), reverse=True)[0])
            self.scan_cli_path = os.path.join(self.scan_cli_home, self.scan_cli_directory)
            self.sig_scanner_found = True
        except IndexError:
            logging.warning("Scan cli not found at location: {}".format(self.scan_cli_home))

    def find_current_sig_scanner(self):
        """
        check if the sig scanner for the current black duck version is already on the system
        """
        latest_sig_scanner_version = self.hub_api.get_latest_scan_cli_version()
        self.scan_cli_directory = 'scan.cli-'
        if latest_sig_scanner_version:
            logging.debug("Found latest sig scanner version: {}".format(latest_sig_scanner_version))
            self.scan_cli_directory += latest_sig_scanner_version
        else:
            logging.debug("Did not find latest sig scanner version - defaulting to Black Duck version")
            self.scan_cli_directory += self.hub_api.get_hub_version()
        self.scan_cli_path = os.path.join(self.scan_cli_home, self.scan_cli_directory)
        if os.path.exists(self.scan_cli_path):
            logging.info("Scan cli has been found, will not be downloaded. Location: {}".format(self.scan_cli_path))
            self.sig_scanner_found = True
            if self.offline_mode:
                logging.warning("Scan cli not found in offline mode at location {}".format(self.scan_cli_path))

    def download_sig_scanner(self):
        """
        Download the signature scanner
        """
        logging.debug("Downloading the signature scanner...")
        logging.debug("scan cli directory is {}".format(self.scan_cli_directory))
        logging.debug("scan cli home is {}".format(self.scan_cli_home))

        sig_scanner_url = self.get_sig_scanner_download_url()

        logging.info("The signature scanner will be downloaded to {}".format(self.scan_cli_home))

        response = self.hub.session.get(sig_scanner_url, allow_redirects=True)

        open(os.path.join(self.scan_cli_home, 'sig-scanner.zip'), 'wb').write(response.content)
        with MyZipFile(os.path.join(self.scan_cli_home, 'sig-scanner.zip'), 'r') as zip_obj:
            zip_obj.extractall(self.scan_cli_home)

        self.sig_scanner_found = True

    @staticmethod
    def json_splitter(scan_path, max_node_entries=200000, max_scan_size=4750000000):
        """
        Splits a json file into multiple jsons so large scans can be broken up with multi-part uploads
        Modified from source: https://github.com/blackducksoftware/json-splitter

        :param scan_path: the path to the json file to split
        :param max_node_entries: the max node entries per scan
        :param max_scan_size: the max size of any single scan in bytes
        :return: a list of the newly generated json files to upload
        """
        new_scan_files = []
        file_split = "file://"

        with open(scan_path, 'r') as f:
            scan_data = json.load(f)

        data_length = len(scan_data['scanNodeList'])

        scan_size = sum(node['size'] for node in scan_data['scanNodeList'] if node['uri'].startswith(file_split))

        if scan_size < max_scan_size:
            return [scan_path]

        logging.info("Source directory greater than 4.75GB. Splitting the json.")

        scan_name = scan_data['name']
        scan_node_list = scan_data.pop('scanNodeList')
        scan_data.pop('scanProblemList')
        scan_data['scanProblemList'] = []
        base = scan_node_list[0]

        # Computing split points for the file
        scan_chunk_size = 0
        scan_chunk_nodes = 0
        split_at = [0]
        for i in range(0, data_length - 1):
            if scan_chunk_size + scan_node_list[i + 1][
                'size'] > max_scan_size or scan_chunk_nodes + 1 > max_node_entries:
                scan_chunk_size = 0
                scan_chunk_nodes = 0
                split_at.append(i)
            if scan_node_list[i]['uri'].startswith(file_split):
                scan_chunk_size = scan_chunk_size + scan_node_list[i]['size']
            scan_chunk_nodes += 1

        # Create array of split points shifting by one position
        split_to = split_at[1:]
        split_to.append(data_length - 2)  # don't include the last entry because it's the one for the entire zip archive

        # Splitting and writing the chunks
        new_scan_path = scan_path.split('.json')[0]
        for i in range(len(split_at)):
            logging.debug("Processing range {}, {}".format(split_at[i], split_to[i]))
            # for i in range(0, dataLength, maxNodeEntries):
            node_data = scan_node_list[split_at[i]:split_to[i]]
            if i > 0:
                node_data.insert(0, base)
            # scanData['baseDir'] = baseDir + "-" + str(i)
            scan_data['scanNodeList'] = node_data
            scan_data['name'] = scan_name + "-" + str(split_at[i])
            filename = new_scan_path + "-" + str(split_at[i]) + '.json'
            with open(filename, 'w') as outfile:
                json.dump(scan_data, outfile)
            scan_data.pop('scanNodeList')
            new_scan_files.append(filename)

        return new_scan_files

    @staticmethod
    def bdio_splitter(scan_path, sig_scan_output_directory, project_version_name, project_name, max_chunk_nodes=3000, max_file_entries=100000):
        p_key = 'https://blackducksoftware.github.io/bdio#hasParentId'
        type_project = "https://blackducksoftware.github.io/bdio#Project"
        type_name = "https://blackducksoftware.github.io/bdio#hasName"
        type_version = "https://blackducksoftware.github.io/bdio#hasVersion"
        outdir = sig_scan_output_directory + '/bdio_files/' + os.path.basename(scan_path.split('.bdio')[0])
        new_scan_files = []
        logging.debug("outdir is {}".format(outdir))
        logging.debug("scan_path is {}".format(scan_path))
        with tempfile.TemporaryDirectory() as tmpdirname:
            with zipfile.ZipFile(scan_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)
            content = dict()
            for filename in os.listdir(tmpdirname):
                fpath = os.path.join(tmpdirname, filename)
                if os.path.isfile(fpath):
                    with open(fpath) as f:
                        content[filename] = json.load(f)
            header = content['bdio-header.jsonld']
            graph = []
            for key in content.keys():
                graph.extend(content[key]['@graph'])

            graph_entries_with_no_parent = [d for d in graph if not d.get(p_key)]
            graph_entries_with_parent = [d for d in graph if d.get(p_key)]
            sorted_graph = sorted(graph_entries_with_parent, key=lambda x: x[p_key][0]['@value'])
            num_source_entries = len(sorted_graph)
            sorted_parent_ids = [int(id[p_key][0]['@value']) for id in sorted_graph]
            sorted_node_ids = [int(id['@id'][id['@id'].index('scanNode-') + 9:1000]) for id in sorted_graph]
            offset = 0
            size = max_file_entries
            max_nodes_per_entry_file = max_chunk_nodes
            part = 0
            first_part = max_nodes_per_entry_file * 2
            current_chunk = sorted_graph[:first_part]
            logging.debug("length of current chunk is {}".format(len(current_chunk)));

            while len(current_chunk) > 0:
                parent_ids = [id[p_key][0]['@value'] for id in current_chunk]
                node_ids = [int(id['@id'][id['@id'].index('scanNode-') + 9:1000]) for id in current_chunk]
                missing_parent_ids = list(set(parent_ids).difference(node_ids))
                if -1 in missing_parent_ids:
                    missing_parent_ids.remove(-1)
                backfill = []
                for parent_id in missing_parent_ids:
                    while parent_id > 0:
                        parent = sorted_graph[sorted_node_ids.index(parent_id)]
                        parent_id = parent[p_key][0]['@value']
                        if parent_id not in backfill:
                            backfill.append(parent_id)
                backfill.extend(missing_parent_ids)
                for i in backfill:
                    current_chunk.append(sorted_graph[sorted_node_ids.index(i)])
                part_name = "_part{:02d}".format(part)
                if project_version_name:
                    part_name = f"_{project_version_name}{part_name}"
                if project_name:
                    part_name = f"_{project_name}{part_name}"

                part_uuid = uuid.uuid4().urn
                header_copy = copy.deepcopy(header)
                project_entry_copy = copy.deepcopy(graph_entries_with_no_parent[0])

                header_copy['@id'] = part_uuid
                name = header_copy[type_name][0]['@value']
                index = name.find(' -SIG')
                if index > 0:
                    updated_name = name[:index] + part_name + name[index:]
                else:
                    updated_name = name + part_name
                header_copy[type_name][0]['@value'] = updated_name

                entry_type = project_entry_copy['@type']
                if entry_type == type_project:
                    pass
                if project_name:
                    project_entry_copy[type_name][0]['@value'] = project_name
                if project_version_name:
                    project_entry_copy[type_version][0]['@value'] = project_version_name
                output_path = os.path.join(outdir, part_name)

                headerfilename = 'bdio-header.jsonld'
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                headerfilepath = os.path.join(output_path, headerfilename)
                with open(headerfilepath, "w") as f:
                    json.dump(header_copy, f, indent=1)

                entry_object = dict()
                entry_object['@id'] = header_copy['@id']
                entry_object['@type'] = header_copy['@type']
                offset_entry_file = 0
                size_entry_file = max_nodes_per_entry_file
                entry_number = 0
                current_slice = current_chunk[offset_entry_file:size_entry_file]
                while len(current_slice) > 0:
                    entry_object['@graph'] = current_slice
                    entry_object['@graph'].insert(0, project_entry_copy)
                    entryfilename = 'bdio-entry-{:02d}.jsonld'.format(entry_number)
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    entryfilepath = os.path.join(output_path, entryfilename)
                    with open(entryfilepath, "w") as f:
                        json.dump(entry_object, f, indent=1)
                    entry_number += 1
                    current_slice = current_chunk[size_entry_file * entry_number:size_entry_file * (entry_number + 1)]

                    current_slice_val_beg = size_entry_file * entry_number
                    current_slice_val_end = size_entry_file * (entry_number + 1);
                    logging.debug(
                        "current slice begin is {} and end is {}".format(current_slice_val_beg, current_slice_val_end));

                current_chunk = sorted_graph[size * part + first_part:size * (part + 1) + first_part]
                current_chunk_begin = size * part + first_part
                current_chunk_end = size * (part + 1) + first_part
                logging.debug("next graph size begin {} and end {}".format(current_chunk_begin, current_chunk_end));
                part += 1

                zip_path = outdir + part_name + '.bdio'
                with zipfile.ZipFile(zip_path, 'w') as zip_object:
                    for filename in os.listdir(output_path):
                        file_path = os.path.join(output_path, filename)
                        logging.debug("adding file {} to zip zip_path {}".format(file_path, zip_path))
                        logging.debug("os.path.basename(file_path) is {}".format(os.path.basename(file_path)))
                        zip_object.write(file_path, os.path.basename(file_path))
                new_scan_files.append(zip_path)
        logging.debug("new scan files are {}".format(new_scan_files))
        return new_scan_files


    def get_java_and_standalone_jar_paths(self):
        """
        Get the paths to the signature scanner java home and the sig scanner standalone jar
        """
        standalone_jar_path = None
        if self.os_dist.lower() == 'mac':
            java_path = os.path.join(self.scan_cli_path, 'jre', 'Contents', 'Home', 'bin', 'java')
        else:
            java_path = os.path.join(self.scan_cli_path, 'jre', 'bin', 'java')
        try:
            standalone_jar_path = glob.glob(os.path.join(self.scan_cli_path, 'lib', '*-standalone.jar'))[0]
            logging.debug("standalone jar path is {}".format(standalone_jar_path))
        except IndexError:
            logging.error("scan cli jar not found at location: {}".format(self.scan_cli_path))
        return java_path, standalone_jar_path

    def build_sig_scanner_command(self):
        """
        Construct the signature scanner command to run
        """
        java_path, standalone_jar_path = self.get_java_and_standalone_jar_paths()
        sig_scanner_command = '"{}" -Done-jar.silent=true -Done-jar.jar.path="{}"{} -Xmx4096m -jar "{}" --no-prompt --project "{}" --release "{}" --name "{}" --individualFileMatching=ALL --binaryAllowedList h,hpp,cpp,c '.format(
            java_path,
            os.path.join(self.scan_cli_path, 'lib', 'cache', 'scan.cli.impl-standalone.jar'),
            self.proxy_settings,
            standalone_jar_path,
            self.project_name, self.project_version_name,
            self.code_location_name)

        if self.offline_mode:
            sig_scanner_command += '--dryRunWriteDir "{}" '.format(self.sig_scan_output_directory)
        else:
            bd_url = self.hub_api.bd_url.split(':{}'.format(self.port))[0]
            if self.url_split in bd_url:
                scheme, host = bd_url.split(self.url_split)
                sig_scanner_command += '--scheme {} --host {} --port {} '.format(scheme, host, self.port)
                if self.insecure:
                    sig_scanner_command += '--insecure '
                self.upload_dry_run = False
            else:
                logging.warning("Black Duck URL could not be parsed for scheme/host - will do dryrun scan instead")
                self.upload_dry_run = True
        if self.verbose:
            sig_scanner_command += '-v '
        if self.additional_sig_scan_args:
            sig_scanner_command += '{} '.format(self.parse_additional_args())

        logging.debug("hub version is {}".format(self.hub_version))
        ## if offline mode - default to --bdio2, so splitter support is present
        ## if online mode - having --bdio2 doesn't support snippet-matching, so remember not to add it in online mode later on
        if self.offline_mode:
            sig_scanner_command += '--bdio2 '

        output_dir = '"{}"'.format(
            self.sig_files_output_path if self.expand_sig_files else (self.sig_scan_zip_output_directory))
        sig_scanner_command += output_dir

        logging.info("sig scanner command is {}".format(sig_scanner_command))
        return sig_scanner_command

    def parse_additional_args(self):
        """
        Parse the self.additional_sig_scan_args string and return a string with the arguments, which may contain spaces,
        properly quoted.

        The entire string can't be quoted because it may contain multiple parameters. Only args should be quoted,
        not parameters.

        Example input: --parameter0 argument with spaces --parameter1 argumentwithoutspace --parameter2 argument--with--double--dashes --parameter3
        Example output: --parameter0  "argument with spaces" --parameter1  "argumentwithoutspace" --parameter2  "argument--with--double--dashes" --parameter3
        """
        additional_sig_scan_args_str_with_quotes = ''
        delim = '--'
        additional_sig_scan_args_lst = re.split('( {})'.format(delim), ' {}'.format(self.additional_sig_scan_args))

        while additional_sig_scan_args_lst:
            item = additional_sig_scan_args_lst.pop(0).strip()
            if item == delim:
                parameter_with_args = additional_sig_scan_args_lst.pop(0).split()
                parameter = delim + parameter_with_args.pop(0)
                additional_sig_scan_args_str_with_quotes += '{} '.format(
                    parameter)  # parameter does not need to be escaped, will never contain spaces

                # handle args, which may contain spaces that need to be escaped
                if parameter_with_args:
                    additional_sig_scan_args_str_with_quotes += ' "{}" '.format(' '.join(parameter_with_args))

        return additional_sig_scan_args_str_with_quotes

    def run_sig_scanner(self):
        """
        Scan the zip files created by zip_files()
        """
        logging.info("Running the signature scanner")
        if os.path.exists(os.path.join(self.sig_scan_output_directory, 'data')):
            shutil.rmtree(os.path.join(self.sig_scan_output_directory, 'data'))  # remove data directory if exists
        env = dict(os.environ)
        env['BD_HUB_TOKEN'] = self.api_token
        scan_cli_opts = os.getenv('SCAN_CLI_OPTS', '')
        if scan_cli_opts != '':
            self.proxy_settings = " {}".format(scan_cli_opts)
        sig_scanner_command = self.build_sig_scanner_command()
        util.run_cmd(sig_scanner_command, env=env, curdir=self.sig_scan_output_directory)
        logging.info("Finished running the signature scanner")

    def upload_sig_json_results(self):
        """
        Upload the json results of the sig scanner to Black Duck to create a BOM. Used if Black Duck version < 2021.10.0.
        """
        logging.info("Uploading signature scan file {}".format(self.json_file))
        try:
            if self.expand_sig_files:
                sig_path = util.get_dir_size(self.sig_files_output_path)
                logging.debug("sig_path size is {}".format(sig_path))
            else:
                sig_path = os.stat(self.zip_output_path).st_size
                logging.debug("sig_path size is {}".format(sig_path))
        except FileNotFoundError as e:
            util.error_and_exit(
                "FileNotFound error, please make sure yaml file is same in offline/online mode: {}".format(e))
        if self.disable_bdio_json_splitter or (sig_path < self.json_splitter_limit):
            response = util.upload_scan(self.json_file, self.hub, self.hub_api.bd_url)
            if not response.ok:
                logging.error("Problem uploading the json file -- (Response({}): {})".format(response.status_code,
                                                                                             response.text))
        else:
            json_lst = self.json_splitter(self.json_file, max_scan_size=self.json_splitter_limit)
            for j in json_lst:
                response = util.upload_scan(j, self.hub, self.hub_api.bd_url)
                logging.info('Uploading {} of {} json files'.format(str(json_lst.index(j) + 1), str(len(json_lst))))
                if json_lst.index(j) < len(json_lst) - 1:
                    time.sleep(self.sleep_interval)
                if not response.ok:
                    logging.error("Problem uploading the json file -- (Response({}): {})".format(response.status_code,
                                                                                                 response.text))

    def upload_sig_bdio_results(self):
        """
        Upload the bdio results of the sig scanner to Black Duck to create a BOM. Used if Black Duck version >= 2021.10.0.
        """
        try:
            if self.expand_sig_files:
                sig_path = util.get_dir_size(self.sig_files_output_path)
                logging.debug("sig_path size is {}".format(sig_path))
                logging.debug("sig files output path is {}".format(self.sig_files_output_path))
            else:
                sig_path = os.stat(self.zip_output_path).st_size
                logging.debug("Sig_path size is {}".format(sig_path))
                logging.debug("sig files output path is {}".format(self.zip_output_path))
        except FileNotFoundError as e:
            util.error_and_exit(
                "FileNotFound error, please make sure yaml file is same in offline/online mode: {}".format(e))

        # if file is less than 5gb - upload bdio file
        logging.debug("self.json_splitter_limit is {}".format(self.json_splitter_limit))
        if self.disable_bdio_json_splitter or (sig_path < self.json_splitter_limit):
            logging.debug("uploading bdio without splitter")
            self.upload_bdio_file()
        else:
            logging.debug("using bdio splitter to upload")
            bdio_lst = self.bdio_splitter(self.bdio_file, self.sig_scan_output_directory, self.project_version_name, self.project_name, max_chunk_nodes=self.bdio_split_max_chunk_nodes, max_file_entries=self.bdio_split_max_file_entries)
            for bd in bdio_lst:
                self.bdio_file = bd
                logging.debug("self.bdio_file is {}".format(self.bdio_file))
                self.upload_bdio_file()



    def upload_bdio_file(self):
        ext = "intelligent-persistence-scans"
        endpoint = '{}/api/{}'.format(self.hub_api.bd_url, ext)
        with tempfile.TemporaryDirectory() as tmpdirname:
            with zipfile.ZipFile(self.bdio_file, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)
            logging.debug("files present here are {}".format(os.listdir(tmpdirname)))

            jsonld_headers_path = os.path.join(tmpdirname, 'bdio-header.jsonld')
            jsonld_files_lst = sorted(glob.glob('{}/bdio-entry*.jsonld'.format(tmpdirname)))
            logging.info("Uploading signature scan file {}".format(self.bdio_file))

            # make sure headers file is uploaded first
            headers = dict()
            headers['Content-type'] = "application/vnd.blackducksoftware.intelligent-persistence-scan-1-ld-2+json"
            headers['User-Agent'] = "SCAN_CLI"

            logging.info("Uploading headers file with path {}".format(jsonld_headers_path))

            with open(jsonld_headers_path, 'rb') as f:
                response = self.hub.session.post(endpoint, headers=headers, data=f, timeout=600)
            if 'Location' not in response.headers:
                logging.error("Location was not in response headers. Can not proceed.")
                return None

            location = response.headers['Location']
            logging.info(
                "Headers file uploaded successfully, proceeding to upload remaining scans using URL {}".format(
                    location))

            total_files_count = len(jsonld_files_lst)
            headers['X-BD-MODE'] = "append"
            headers['X-BD-DOCUMENT-COUNT'] = str(len(jsonld_files_lst))

            for f in jsonld_files_lst:
                logging.info("Uploading {} of {} bdio entry jsonld files with name {}...".format(
                    str(jsonld_files_lst.index(f) + 1), str(total_files_count), f))
                with open(f, 'rb') as d:
                    response = self.hub.session.put(location, headers=headers, data=d)
                    if not response.ok:
                        logging.error(
                            "Problem uploading the bdio file -- (Response({}): {})".format(response.status_code,
                                                                                           response.text))
                        self.logger.log_warning(response.headers)

            headers['X-BD-MODE'] = "finish"
            r = self.hub.session.put(location, headers=headers, verify=not self.insecure)

            if not r.ok:
                util.error_and_exit(
                    "error occurred when uploading signature scanner jsonld file -- (Response({}): {})".format(r.status_code, r.text))

    def find_dryrun_files(self):
        """
        Find the path to the dryrun file created by the sig scanner. Will be a BDIO if >=2021.10.0 or JSON if <2021.10.0.
        """
        hub_version = self.hub_api.get_hub_version()
        major, minor, patch = hub_version.split('.')

        if self.version_grt:
            bdio_files = glob.glob(os.path.join(self.sig_scan_output_directory, 'data', '*.bdio'))
            if bdio_files:
                bdio_files.sort(reverse=True)
                self.bdio_file = bdio_files[0]
                return True

        json_files = glob.glob(os.path.join(self.sig_scan_output_directory, 'data', '*.json'))
        if json_files:
            json_files.sort(reverse=True)
            self.json_file = json_files[0]
            return True
        return False

    def get_offline_files_in_dir(self):
        """
        For use if running with offline files. Find the exploded directory created in a previous run, and if it exists, check if
        the /data/ directory that contains the json or bdio scan file exists. If not, run the sig scanner.
        """
        # finding if zip file is present
        logging.info("Attempting to use offline files for signature scanner file at location: {}".format(
            self.sig_files_output_path))

        if os.path.exists(self.sig_files_output_path):
            logging.info("Found signature scanner files at location: {}".format(self.sig_files_output_path))
            return True
        else:
            logging.error(
                "Unable to find previously generated offline signature files for signature scanner, set use_offline_files to false to generate new ones.")
            return False

    def get_offline_zip_file(self):
        """
        For use if running with offline files. Find the zip file create in a previous run, and if it exists, check if
        the /data/ directory that contains the json or bdio scan file exists. If not, run the sig scanner.
        """
        # finding if zip file is present
        logging.info("Attempting to use offline files for signature scanner zip file at location: {}".format(
            self.zip_output_path))

        if os.path.exists(self.zip_output_path):
            logging.info("Found signature scanner zip file at location: {}".format(self.zip_output_path))
            return True
        else:
            logging.error(
                "Unable to find previously generated offline zip files for signature scanner, set use_offline_files to false to generate new ones.")
            return False


    def run(self):
        """
        entry point
        """
        # find the most recent available sig scanner if it is already downloaded
        if self.offline_mode:
            self.find_any_sig_scanner()
        if not self.offline_mode:
            self.find_current_sig_scanner()
            # download the sig scanner if necessary
            if not self.sig_scanner_found:
                self.download_sig_scanner()
            logging.info("Will wait {} seconds between scan uploads if there are multiple scans".format(
                str(self.sleep_interval)))
            logging.info("Results will be uploaded to {}".format(self.hub_api.bd_url))
            logging.info(
                "Results will be mapped to project {} version {} and code location {}".format(self.project_name,
                                                                                              self.project_version_name,
                                                                                              self.code_location_name))

        # zip the files or copy files to exploded directory in online mode
        if not self.use_offline_files:
            self.copy_files_to_dir() if self.expand_sig_files else self.zip_files()
        # if we don't find previously generated files in offline mode run sig scanner
        if self.use_offline_files:
            if self.expand_sig_files and not (self.get_offline_files_in_dir() or self.find_dryrun_files()):
                return
            if not self.expand_sig_files and not (self.get_offline_zip_file() or self.find_dryrun_files()):
                return

        # run the sig scanner
        if self.use_offline_files:
            # if previous files are generated in offline mode, upload them, else run signature scanner if scan-cli is present
            if self.find_dryrun_files():
                logging.info("Using old signature scan from previous offline scan at location {}".format(
                    self.sig_scan_output_directory))
            elif self.scan_cli_path:
                self.run_sig_scanner()
        elif self.scan_cli_path:
            self.run_sig_scanner()

        # upload the dryrun files
        if self.upload_dry_run:
            if not self.find_dryrun_files():
                logging.error(
                    "The signature scan file was not generated. There will not be signature matching results.")
            if self.bdio_file:
                self.upload_sig_bdio_results()
            elif self.json_file:
                self.upload_sig_json_results()
            else:
                logging.error("No dryrun scan file was found")

        if self.offline_mode:
            logging.debug("Signature scanner was run in offline mode. Files are stored at Location: {}".format(
                self.sig_scan_output_directory))
