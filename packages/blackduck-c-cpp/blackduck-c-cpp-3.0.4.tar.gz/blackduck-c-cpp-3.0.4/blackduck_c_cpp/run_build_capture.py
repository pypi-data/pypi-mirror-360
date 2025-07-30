"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""
import asyncio
import glob
import json
import logging
import os
import platform
import re
import shlex
import stat
import subprocess
import sys
from datetime import datetime
from os.path import expanduser
from blackduck_c_cpp.util import util
from blackduck_c_cpp.util.c_arg_parser import C_Parser
from blackduck_c_cpp.pkg_manager.pkg_manager_detector import PkgDetector
from blackduck_c_cpp.pkg_manager.pkg_manager_bom import PkgManagerBom
from blackduck_c_cpp.bdba.upload_bdba import BDBAApi
from blackduck_c_cpp.sig_scanner.emit_wrapper import EmitWrapper
from blackduck_c_cpp.bdio.bdio2_python_transformer import BDIO2Transformer
from blackduck_c_cpp.sig_scanner.run_sig_scanner import SigScanner
from blackduck_c_cpp.util.hub_api import HubAPI
from blackduck_c_cpp.coverity_json.cov_json_parse import CovJsonParser
from blackduck_c_cpp.util.cov_install import CoverityInstall
import shutil
from importlib.metadata import version as importlib_version

"""
This class will run coverity build capture for the supplied build command.
It assumes that any setup and configuration for the build has already taken place 
prior to calling this code.
"""


class RunBuildCapture(object):

    def __init__(self, my_args, log_path, blackduck_output_dir):
        self.my_args = my_args
        self.start_time = datetime.now()
        self.blackduck_c_cpp_version = self.get_package_version()
        self.home = expanduser("~")
        # Ensure backward compatibility for migration from .synopsys to .blackduck
        self.migrate_old_directory()
        self.bld_dir = util.get_absolute_path(self.my_args.args.build_dir)
        self.bld_cmd = self.my_args.args.build_cmd
        self.hub_project_name = self.my_args.args.project_name
        self.hub_project_vers = shlex.quote(self.my_args.args.project_version)
        if self.my_args.args.cov_output_dir:
            # if cov_output_dir is given by user, check if it is idir or parent of idir by verifying if build-log.txt is present in it
            if os.path.exists(os.path.join(util.get_absolute_path(self.my_args.args.cov_output_dir), "build-log.txt")):
                logging.debug("given cov_output_dir path is idir")
                self.cov_prj = os.path.dirname(util.get_absolute_path(self.my_args.args.cov_output_dir))
                self.cov_dir = util.get_absolute_path(self.my_args.args.cov_output_dir)

            else:
                logging.debug("given cov_output_dir path is parent of idir")
                self.cov_prj = util.get_absolute_path(self.my_args.args.cov_output_dir)
                self.cov_dir = os.path.join(self.cov_prj, "idir")
        else:
            self.cov_prj = os.path.join(self.home,".blackduck","blackduck-c-cpp","output",self.hub_project_name)
            self.cov_dir = os.path.join(self.cov_prj, "idir")

        self.blackduck_output_dir = util.get_absolute_path(blackduck_output_dir)
        self.project_group_name = my_args.args.project_group_name
        self.project_description = my_args.args.project_description
        self.skip_build = my_args.args.skip_build
        self.port = my_args.args.port
        self.bd_url = shlex.quote(self.my_args.args.bd_url.strip('/'))
        self.bd_url_with_port = '{}:{}'.format(self.bd_url, self.port)
        self.codelocation_name = shlex.quote(
            self.my_args.args.codelocation_name) if self.my_args.args.codelocation_name else "{}/{}".format(
            self.hub_project_name, self.hub_project_vers)
        self.additional_sig_scan_args = self.my_args.args.additional_sig_scan_args
        self.expand_sig_files = self.my_args.args.expand_sig_files
        self.additional_coverity_params = self.my_args.args.additional_coverity_params
        self.api_token = shlex.quote(self.my_args.args.api_token) if self.my_args.args.api_token else os.environ.get(
            'BLACKDUCK_API_TOKEN') or os.environ.get('BD_HUB_TOKEN')
        if self.api_token is None:
            logging.error("No api token found. Please provide an api token.")
            sys.exit(1)
        self.insecure = True if self.my_args.args.insecure else False
        self.force = True if self.my_args.args.force else False
        self.skip_transitives = self.my_args.args.skip_transitives
        self.skip_includes = self.my_args.args.skip_includes
        self.skip_dynamic = self.my_args.args.skip_dynamic
        self.use_offline_files = self.my_args.args.use_offline_files
        self.offline_mode = self.my_args.args.offline
        self.verbose = self.my_args.args.verbose
        self.scan_cli_dir = util.get_absolute_path(
            self.my_args.args.scan_cli_dir) if self.my_args.args.scan_cli_dir is not None else self.blackduck_output_dir
        self.cov_configure_args = my_args.args.cov_configure_args
        self.run_modes = list(map(lambda mode: mode.lower(), map(lambda s: re.sub("[\"\']", "", s),
                                                                 map(str.strip, self.my_args.args.modes.split(",")))))
        if self.my_args.args.set_coverity_mode and self.my_args.args.set_coverity_mode.lower() == 'cov-build':
            self.cov_mode = self.my_args.args.set_coverity_mode.lower()
        else:
            self.cov_mode = None;
        self.cov_version = None;
        if self.my_args.args.force_pull_coverity_vers and self.my_args.args.force_pull_coverity_vers.lower() in (
        'latest', 'old'):
            self.force_pull_coverity_vers = self.my_args.args.force_pull_coverity_vers.lower()
            if self.my_args.args.coverity_root:
                logging.warning("coverity root specified by user, please remove setting force_pull_coverity_vers")
        else:
            self.force_pull_coverity_vers = None

        logging.debug("run modes is {}".format(self.run_modes))
        self.PKG_MGR_MODE = 'pkg_mgr'
        self.SIG_MODE = 'sig'
        self.BDBA_MODE = 'bdba'
        self.ALL_MODE = 'all'
        self.COV_CONF_FILE = "bld.xml"
        self.hub_api = HubAPI(self.bd_url_with_port, self.api_token, self.insecure)
        self.log_path = util.get_absolute_path(log_path)
        self.platform_name = platform.system().lower()
        self.client_version = ''
        self.cov_home = self.set_coverity_root()
        self.cov_bin = os.path.join(self.cov_home, "bin")
        self.build_log = os.path.join(self.cov_dir, "build-log.txt")
        self.binary_files_list = os.path.join(self.blackduck_output_dir, "all_binary_paths.txt")
        self.json_grep_files_list = os.path.join(self.blackduck_output_dir, "json_grep_files_diff.txt")
        self.unresolved_files_list = os.path.join(self.blackduck_output_dir, "unresolved_file_paths.txt")
        self.resolved_files_list = os.path.join(self.blackduck_output_dir, "resolved_file_paths.txt")
        self.resolved_cov_files_list = os.path.join(self.blackduck_output_dir, "resolved_cov_file_paths.txt")
        self.unresolved_cov_files_list = os.path.join(self.blackduck_output_dir, "unresolved_cov_file_paths.txt")
        self.cov_json_file_path = os.path.join(self.blackduck_output_dir, "cov_emit_links.json")
        self.bazel = my_args.args.bazel

    def __enter__(self):
        if not self.offline_mode:
            self.hub_api.create_or_verify_project_version_exists(self.hub_project_name, self.hub_project_vers,
                                                                 self.project_group_name, self.project_description)
        if not os.path.exists(self.cov_dir):
            os.makedirs(self.cov_dir)

        logging.info("RUNNING BLACKDUCK-C-CPP VERSION {}".format(self.blackduck_c_cpp_version))
        logging.info("Output log is written to file {}".format(os.path.join(self.log_path)))
        logging.info("coverity output files will be in {}".format(self.cov_dir))

        args_to_print = self.my_args.args
        args_to_print.api_token = '*********'
        logging.debug("Arguments passed into blackduck-c-cpp are {}".format(args_to_print))

        offline_yaml_location = os.path.join(self.blackduck_output_dir, "offline_config.yaml")
        if self.offline_mode:
            logging.debug("Storing config file to location : {}".format(offline_yaml_location))
            with open(offline_yaml_location, 'w') as f:
                json.dump(self.my_args.args.__dict__, f, indent=2)
        if self.use_offline_files:
            logging.warning(
                "Please make sure skip_* parameters are kept exactly same as in offline mode from offline configuration file {}".format(
                    offline_yaml_location))

        if self.use_offline_files and (self.offline_mode or not self.skip_build):
            util.error_and_exit("Cannot set use_offline_files=True and offline=True/skip_build=False")

        if self.insecure:
            logging.warning("SSL verification has been disabled with the --insecure flag")

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            print(f'exc_type: {exc_type}')
            print(f'exc_value: {exc_value}')
            print(f'exc_traceback: {exc_traceback}')


    @staticmethod
    def handle_uncaught_exp(type, value, traceback):
        logging.error("Logging an uncaught exception", exc_info=(type, value, traceback))

    def get_phase_status_dict(self):
        """
        Read the log file and check for errors in each section
        :return: a dict of each phase and its status (SUCCESS or ERROR)
        """
        phase_dict = {}
        phase_pattern = r'Phase: (.*) '
        error_pattern = r'ERROR: (.*)$'
        # handle error_pattern by recognizing
        try:
            with open(self.log_path, 'r') as f:
                contents = f.read()
        except:
            logging.error("Could not open log file to generate a status report - verify directory permissions")
            return phase_dict

        phases = re.findall(phase_pattern, contents, flags=re.MULTILINE)
        log_sections = re.split(phase_pattern, contents)

        for p in phases:
            if 'Blackuck-c-cpp Status Report' not in p:
                content_index = log_sections.index(p) + 1
                error_matches = re.findall(error_pattern, log_sections[content_index], flags=re.MULTILINE)
                if not error_matches:
                    phase_dict[p] = 'SUCCESS'
                if error_matches:
                    phase_dict[p] = 'ERROR - SEE LOGS AT {} FOR DETAILS'.format(self.log_path)
        return phase_dict

    @staticmethod
    def get_package_version():
        """
        Get the version of blackduck-c-cpp that's being run
        Will only work if the blackduck-c-cpp module has been installed - will return unknown if running from source
        code that's been added to PYTHONPATH
        :return: the blackduck-c-cpp version
        """
        try:
            version_c_cpp_tool = importlib_version('blackduck-c-cpp')
        except Exception as e:
            logging.warning("unable to get version of blackduck-c-cpp from importlib_metadata - {}".format(e))
            try:
                version_c_cpp_tool = __import__('blackduck_c_cpp').__version__
            except Exception as e:
                logging.warning("unable to get version of blackduck-c-cpp - {}".format(e))
                version_c_cpp_tool = 'UNKNOWN'
        return version_c_cpp_tool

    @staticmethod
    def log_phase(phase):
        """
        Call at the beginning of each phase to log the current process being run
        :param: the current phase
        """
        print()  # line break between phases for readability
        logging.info("******************************   Phase: {} ***********************************".format(phase))


    def migrate_old_directory(self):
        """
        Check if the old `.synopsys/blackduck-c-cpp` directory exists.
        If it does, move its contents to the new `.blackduck/blackduck-c-cpp` directory.
        """
        old_dir = os.path.join(self.home, ".synopsys", "blackduck-c-cpp")
        new_dir = os.path.join(self.home, ".blackduck", "blackduck-c-cpp")

        if os.path.exists(old_dir):
            logging.info(f"Found old directory at {old_dir}. Migrating to {new_dir}.")
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            for item in os.listdir(old_dir):
                old_item_path = os.path.join(old_dir, item)
                new_item_path = os.path.join(new_dir, item)
                if os.path.exists(new_item_path):
                    renamed_path = os.path.join(new_dir, f"{item}_old")
                    logging.warning(f"Destination path '{new_item_path}' already exists. Renaming to '{renamed_path}'.")
                    try:
                        shutil.move(old_item_path, renamed_path)
                    except Exception as e:
                        logging.debug(f"Failed to rename '{old_item_path}' to '{renamed_path}': {e}")
                else:
                    logging.info("Moving {} to {}".format(old_item_path, new_item_path))
                    shutil.move(old_item_path, new_item_path)
            # Remove the old directory only if it is empty
            if not os.listdir(old_dir):
                shutil.rmtree(old_dir)
                logging.info(f"Migration from {old_dir} to {new_dir} completed.")
            else:
                logging.warning(f"Old directory {old_dir} is not empty. Please check manually.")
        else:
            logging.debug(f"No old directory found at {old_dir}. Using {new_dir}.")


    def find_bazel_workspace_file(self):
        bazel_workspace_files = glob.glob(os.path.join(self.bld_dir, 'WORKSPACE*'), recursive=False)
        if len(bazel_workspace_files) != 1:
            if not bazel_workspace_files:
                logging.warning(
                    "The Bazel WORKSPACE file was not found so the required modification can't be verified.")
            else:
                logging.warning("Multiple possible WORKSPACE files were found.")
            logging.warning(
                "If the Bazel WORKSPACE file has already been modified manually to work with Coverity, ignore this warning. Otherwise, see the Bazel Setup > Modify project files > Workspace file section in the PyPi documentation for instructions.")
            return None
        return bazel_workspace_files[0]

    def modify_bazel_workspace_file(self):
        """
        Modify the workspace file for bazel build if need be
        """
        bazel_workspace_file = self.find_bazel_workspace_file()
        if bazel_workspace_file:
            with open(bazel_workspace_file, 'r') as f:
                contents = f.read()
                if 'rules_coverity' in contents:
                    logging.debug(
                        "The bazel WORKSPACE file appears to have been already updated to work with Coverity and will not be modified")
                    return
            with open(bazel_workspace_file, 'a') as f:
                logging.info("The bazel WORKSPACE file does not have the required modification and will be updated")
                update_string = 'load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")' + os.linesep \
                                + 'http_archive(' + os.linesep \
                                + '    name="rules_coverity",' + os.linesep \
                                + '    urls=["file:///{}"],'.format(
                    os.path.join(self.cov_home, 'bazel', 'rules_coverity.tar.gz')) + os.linesep \
                                + ')' + os.linesep + os.linesep \
                                + 'load("@rules_coverity//coverity:repositories.bzl", "rules_coverity_toolchains")' + os.linesep \
                                + 'rules_coverity_toolchains()'
                f.write(update_string)
                logging.debug("Text appended to WORKSPACE file:")
                logging.debug(update_string)

    def get_cov_version(self, cov_home):
        cmd = os.path.join(cov_home, "bin", "cov-build") + ' --ident'
        out = subprocess.getstatusoutput(cmd)
        status, cov_version = util.value_getstatusoutput(out)
        if status:
            return cov_version
        else:
            return 'UNKNOWN'

    def set_coverity_root(self):
        self.log_phase("Get coverity root information")
        if self.my_args.args.coverity_root:
            if os.path.exists(self.my_args.args.coverity_root):
                logging.debug("Using coverity package given by user")
                cov_home = util.get_absolute_path(self.my_args.args.coverity_root)
            else:
                logging.warning("Coverity_root given by user does not exist, so using coverity package downloaded by blackduck-c-cpp")
                cov_home = self.coverity_download()
        else:
            cov_home = self.coverity_download()
        logging.info("coverity files are at {}".format(cov_home))
        self.cov_version = self.get_cov_version(cov_home)
        logging.info("COVERITY VERSION IS {}".format(self.cov_version))
        return cov_home

    def coverity_download(self):
        """
        download coverity if cov_root is not given by user
        :return: the files to be zipped by the sig scanner
        """
        start_download = datetime.now()
        logging.debug("Downloading Coverity as coverity_root is not given by user")
        cov_home = os.path.join(expanduser("~"), ".blackduck", "blackduck-c-cpp", "cov-build-capture")
        if not os.path.exists(cov_home):
            os.makedirs(cov_home)
        try:
            blackduck_c_cpp_version_list = list(map(int, self.blackduck_c_cpp_version.split('.')))
            blackduck_version_check = (((blackduck_c_cpp_version_list[0] >= 2) and (blackduck_c_cpp_version_list[1] >= 0) and (
                        blackduck_c_cpp_version_list[2] > 6)) \
                        or (blackduck_c_cpp_version_list[0] >= 3) or (
                                blackduck_c_cpp_version_list[0] > 2 and blackduck_c_cpp_version_list[1] > 1))
        except Exception as e:
            logging.debug("unable to compare blackduck-c-cpp version - {}".format(e))
            blackduck_version_check = False

        if self.force_pull_coverity_vers:
            self.client_version = 'old' if self.force_pull_coverity_vers == 'old' else ''
        else:
            ## If on linux platform, check if glibc version is < 2.18
            if self.platform_name == 'linux':
                vers_major, vers_minor = self.gnu_get_libc_version()
                if (int(vers_major) <= 2 and int(vers_minor) <= 17) or int(vers_major) < 2:
                    logging.warning(
                        "Found glibc version is < 2.18. - found version is {}.{} - downloading older version of coverity".format(
                            vers_major, vers_minor))
                    self.client_version = 'old'
                else:
                    if blackduck_version_check:
                        self.client_version = 'linux64202510'
            else:
                ## if blackduck-c-cpp version is > 2.0.6 -> set clientVersion to linux64202510 or win64202510 or macosx202510 based on platform name,
        # otherwise set clientVersion to empty string
                # convert blackduck version to list and compare
                if blackduck_version_check:
                    if 'windows' in self.platform_name:
                        self.client_version = 'win64202510'
                    elif 'darwin' in self.platform_name:
                        self.client_version = 'macosx202510'
                    else:
                        self.client_version = 'linux64202510'

        CoverityInstall(cov_home, self.hub_api, self.platform_name, self.force, self.client_version)
        end_download = datetime.now()
        logging.debug('Time taken to download coverity files: {}'.format(end_download - start_download))
        return cov_home

    def gnu_get_libc_version(self):
        vers_major, vers_minor = 3, 0
        try:
            try:
                ld_path = os.environ['LD_LIBRARY_PATH']
                ld_lib_paths = ld_path.split(':')
                resolv_ld_vers = list(map(lambda path_1: self.get_version_ld(path_1), filter(
                    lambda path: ('libc-' in os.path.basename(os.path.realpath(path)), ld_lib_paths))))
                ## check for None in list
                resolv_ld_vers_list = list(filter(None, resolv_ld_vers))
                if len(resolv_ld_vers) > 0:
                    return resolv_ld_vers[0].split('.')[0], resolv_ld_vers[0].split('.')[1]
            except Exception as e:
                logging.debug("following exception occurred figuring out glibc version with LD_LIBRARY_PATH: {}. ".format(e))
                if shutil.which('ldd') is not None:
                    ldd_vers = self.ldd_glibc_version()
                    if ldd_vers:
                        return ldd_vers.split('.')[0], ldd_vers.split('.')[1]
                elif shutil.which('ldconfig') is not None:
                    ldconf_vers = self.ldconfig_v()
                    ## check for None in list
                    resolv_ld_vers_list = list(filter(None, ldconf_vers))
                    if len(ldconf_vers) > 0:
                        return ldconf_vers[0].split('.')[0], ldconf_vers[0].split('.')[1]
        except Exception as e:
            logging.warning(
                "following exception occurred while figuring out glib version - {}. So pulling latest coverity version from gcp".format(
                    e))
        return vers_major, vers_minor

    def ldd_glibc_version(self):
        ldd_vers = None
        cmd = 'ldd --version'
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                           encoding=sys.getdefaultencoding(), errors='replace')
        ldd_output = p.stdout.replace(os.linesep, '\n').split('\n')
        for line in ldd_output:
            ldd_vers = self.get_version_ld(line)
            if ldd_vers:
                return ldd_vers
        return ldd_vers

    def ldconfig_v(self):
        ldconf_vers = None
        paths_list = []
        files_list = []
        cmd = 'ldconfig -v'
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                           encoding=sys.getdefaultencoding(), errors='replace')
        ldconfig_output = p.stdout.replace(os.linesep, '\n').split('\n')
        for line in ldconfig_output:
            parts = line.split(':')
            path = parts[0].strip()
            if path.startswith('/'):
                paths_list.append(path)
            if '->' in path:
                if len(paths_list) > 0:
                    files_list.append(paths_list[-1] + '/' + path.split('->')[-1].strip())
        ldconf_vers = list(map(lambda path_1: self.get_version_ld(path_1),
                               filter(lambda path: ('libc-' in os.path.basename(path)), files_list)))
        return ldconf_vers

    def get_version_ld(self, inp):
        try:

            vers = re.search(r"\d+(\.\d+)+", inp).group()
            vers_split = vers.split('.')
            if len(vers_split) > 0:
                return vers
        except AttributeError:
            return None

    def run_build(self, cov_emit_link_path, cov_bld_or_cpt_path, cov_build_run):
        """
        Run cov-build to build the c/cpp target project
        """
        self.log_phase("Starting Build")
        sys.excepthook = self.handle_uncaught_exp
        start_build = datetime.now()
        cov_conf = os.path.join(self.blackduck_output_dir, "conf")
        build_command = self.bld_cmd

        # archive emit directory to keep old results out of new scans
        EmitWrapper(self.cov_home, self.cov_dir, self.blackduck_output_dir, self.platform_name).archive_idir()

        # to write build command to script
        if not os.path.exists(self.bld_cmd):
            if 'windows' in self.platform_name:
                sh_path = os.path.join(self.cov_prj, 'cov-build.bat')
            else:
                sh_path = os.path.join(self.cov_prj, 'cov-build.sh')
            with open(sh_path, 'w') as rsh:
                rsh.write("{}".format(self.bld_cmd))
            st = os.stat(sh_path)
            os.chmod(sh_path, st.st_mode | stat.S_IEXEC)
        else:
            sh_path = self.bld_cmd

        if not os.path.exists(cov_conf):
            os.makedirs(cov_conf)

        logging.debug("PLATFORM NAME IS {}".format(self.platform_name))
        if 'windows' in self.platform_name:
            conf_key = " & "
        else:
            conf_key = " \n "

        if cov_build_run:
            conf_cmd = util.conf_cmd("--clang", self.cov_bin, cov_conf)
            conf_cmd += conf_key + util.conf_cmd("--msvc", self.cov_bin, cov_conf)
            if self.bazel:
                conf_cmd += conf_key + util.conf_cmd("--gcc", self.cov_bin, cov_conf)

            conf_cmd += conf_key + util.conf_cmd("--template --compiler cc --comptype gcc", self.cov_bin, cov_conf)
            conf_cmd += conf_key + util.conf_cmd("--template --compiler *gcc* --comptype gcc", self.cov_bin, cov_conf)
            conf_cmd += conf_key + util.conf_cmd("--template --compiler *c++* --comptype gcc", self.cov_bin, cov_conf)

            conf_cmd += conf_key + util.conf_cmd("--template --compiler ld --comptype ld", self.cov_bin, cov_conf)
            conf_cmd += conf_key + util.conf_cmd("--template --compiler *-ld --comptype ld", self.cov_bin, cov_conf)
            conf_cmd += conf_key + util.conf_cmd("--template --compiler ^ld-* --comptype ld", self.cov_bin, cov_conf)

            conf_cmd += conf_key + util.conf_cmd("--template --compiler ccache --comptype prefix", self.cov_bin,
                                                 cov_conf)
            for compiler, comptype in self.cov_configure_args.items():
                conf_cmd += conf_key + util.conf_cmd(
                    "--template --compiler {} --comptype {}".format(compiler, comptype),
                    self.cov_bin, cov_conf)
        else:
            conf_cnt = 0
            conf_cmd = ''
            for compiler, comptype in self.cov_configure_args.items():
                if (conf_cnt == 0):
                    conf_key = ''
                else:
                    conf_key = '&'
                conf_cmd += conf_key + util.conf_cmd(
                    "--template --compiler {} --comptype {}".format(compiler, comptype),
                    self.cov_bin, cov_conf)
                conf_cnt +=1
            conf_path = os.path.join(cov_conf, self.COV_CONF_FILE)
            conf_ret_code = util.run_cmd(conf_cmd, self.bld_dir)
            if conf_ret_code != 0:
                util.error_and_exit(
                    "Failed to configure coverity compiler properly. Please check the configuration file at {}".format(
                        conf_path))
            if os.path.exists(conf_path) and conf_cmd != '':
                conf_file = " -o capture.compiler-configuration.file=" + '"' + "{}".format(conf_path) + '"'
            else:
                conf_file = ''

        if self.additional_coverity_params:
            cov_add_cmd = ' {}'.format(self.additional_coverity_params)
        else:
            cov_add_cmd = ''

        # cov-build
        if cov_build_run:
            if os.path.exists(cov_emit_link_path):
                self.bld_cmd = '"{}" --emit-link-units -c "{}" --dir "{}" {} '.format(cov_bld_or_cpt_path,
                                                                                      os.path.join(cov_conf, "bld.xml"),
                                                                                      self.cov_dir, cov_add_cmd)
            else:
                self.bld_cmd = '"{}" -c "{}" --dir "{}" {} '.format(cov_bld_or_cpt_path,
                                                                    os.path.join(cov_conf, "bld.xml"),
                                                                    self.cov_dir, cov_add_cmd)

            if self.bazel:
                self.bld_cmd += ' --bazel {}'.format(build_command)
            else:
                self.bld_cmd += ' --record-with-source "{}"'.format(sh_path)

            full_cmd = conf_cmd + conf_key + self.bld_cmd
            logging.info("Build Command: {}".format(self.bld_cmd))
            ret_code = util.run_cmd(full_cmd, self.bld_dir)
            end_build = datetime.now()
            logging.info('Time taken to run build: {}'.format(end_build - start_build))
            if ret_code != 0:
                util.error_and_exit(
                    "Build is not successful, please make sure to check correct configuration is provided and successful build is done- return code {}".format(
                        ret_code))

        else:
            # cov-cli - for versions > 2024.9 -> remove -o analyze.location=connect command
            cov_vers_cli = re.search(r"\d+(\.\d+)+", self.cov_version).group().split('.')
            if (int(cov_vers_cli[0]) >= 2024 and int(cov_vers_cli[1]) >= 9) or int(cov_vers_cli[0]) >= 2025:
                interm_build_cmd = "capture -o capture.languages.include=c-family"
            else:
                interm_build_cmd = "capture -o analyze.location=connect -o capture.languages.include=c-family"

            if os.path.exists(cov_emit_link_path):
                self.bld_cmd = '"{}" {} -o capture.build.cov-build-args=--emit-link-units{} --dir "{}"{}'.format(
                    cov_bld_or_cpt_path,
                    interm_build_cmd,
                    conf_file,
                    self.cov_dir, cov_add_cmd)
            else:
                self.bld_cmd = '"{}" {}{} --dir "{}"{}'.format(
                    cov_bld_or_cpt_path, interm_build_cmd, conf_file,
                    self.cov_dir, cov_add_cmd)

            if self.bazel:
                self.bld_cmd += ' -o capture.build.cov-build-args=--bazel -- {}'.format(build_command)
            else:
                self.bld_cmd += ' -- "{}"'.format(sh_path)
            full_cmd = self.bld_cmd
            logging.info("coverity capture Command: {}".format(full_cmd))
            ret_code = util.run_cmd(full_cmd, self.bld_dir)
            end_build = datetime.now()
            logging.info('Time taken to run build: {}'.format(end_build - start_build))
            if ret_code != 0:
                util.error_and_exit(
                    "coverity capture is not successful, please make sure to check correct configuration is provided and successful build is done- return code {}".format(
                        ret_code))

    def run_cov_emit(self):
        """
        Run cov manage emit
        :return: the files to be zipped by the sig scanner
        :return: the header files on which to run the package manager scan
        """
        self.log_phase("Running Cov Manage Emit")
        start_emit = datetime.now()
        if not self.use_offline_files:
            blackduck_emit_wrapper = EmitWrapper(self.cov_home, self.cov_dir, self.blackduck_output_dir,
                                                 self.platform_name)
            blackduck_emit_wrapper.run_cov_emit()
            emit_wrapper_output_sig = blackduck_emit_wrapper.cov_emit_output_sig
            emit_cov_header_files = blackduck_emit_wrapper.cov_header_files
        else:
            emit_wrapper_output_sig = emit_cov_header_files = None
            if os.path.exists(os.path.join(self.blackduck_output_dir, 'cov_emit_output_files')):
                logging.info("Attempting to use offline files for cov-manage-emit at location: {}".format(
                    os.path.join(self.blackduck_output_dir, 'cov_emit_output_files')))
            else:
                logging.error(
                    "Unable to find previously generated offline files for cov-manage-emit, set use_offline_files to false to generate new ones.")
        end_emit = datetime.now()
        logging.info('Time taken to get emit files: {}'.format(end_emit - start_emit))

        return emit_wrapper_output_sig, emit_cov_header_files

    def run_cov_emit_link(self, cov_manage_emit_path):
        """
        Run cov-emit-link
        """
        self.log_phase("Generating Cov-emit-link json")
        start_emit_link = datetime.now()
        header_files_set = linker_files_set = executable_files_set = set()
        if not self.use_offline_files:
            full_cmd = '"{}" --dir "{}" list-capture-invocations > "{}"'.format(cov_manage_emit_path,
                                                                                self.cov_dir,
                                                                                os.path.join(self.blackduck_output_dir,
                                                                                             "cov_emit_links.json"))
            ret_code = util.run_cmd(full_cmd, self.cov_dir)
            if ret_code == 0:
                cov_parser = CovJsonParser(self.cov_json_file_path)
                header_files_set, linker_files_set, executable_files_set = cov_parser.run()
            else:
                logging.error("coverity json not created successfully- return code {}".format(ret_code))

        end_emit_link = datetime.now()
        logging.info('Time taken to get emit link json files if present: {}'.format(end_emit_link - start_emit_link))
        return header_files_set, linker_files_set, executable_files_set

    def run_get_package_manager_bom(self, emit_cov_header_files, header_files_set, linker_files_set,
                                    executable_files_set):
        """
        Get the package manager BOM, to be written to a BDIO file later in run_bdio_from_package_manager()
        :return: the package manager BOM from which to creaete the BDIO file
        :return: the current OS
        """
        self.log_phase("Getting package manager BOM")
        # if not use_offline_files:
        start_pkg_mgr = datetime.now()
        pkg_manager, os_dist = PkgDetector().get_platform()
        # skips all header files from package manager and bdba matching if skip_includes is True
        if self.skip_includes:
            emit_cov_header_files = []
            header_files_set = []
        if self.use_offline_files:
            emit_cov_header_files = []
            header_files_set = []
        if pkg_manager and os_dist:
            pkg_mgr_bom = PkgManagerBom(pkg_manager,
                                        self.build_log,
                                        self.cov_home,
                                        self.blackduck_output_dir,
                                        os_dist,
                                        self.bld_dir,
                                        self.unresolved_files_list,
                                        self.resolved_files_list,
                                        self.binary_files_list,
                                        self.json_grep_files_list,
                                        self.skip_build,
                                        self.skip_transitives,
                                        self.skip_dynamic,
                                        self.run_modes,
                                        emit_cov_header_files, self.my_args.args.debug, header_files_set,
                                        linker_files_set, executable_files_set, self.resolved_cov_files_list,
                                        self.unresolved_cov_files_list, self.hub_api,
                                        self.offline_mode, self.use_offline_files)
            asyncio.run(pkg_mgr_bom.run())
        else:
            pkg_mgr_bom = None
        end_pkg_mgr = datetime.now()
        logging.info('Time taken to get package manager results: {}'.format(end_pkg_mgr - start_pkg_mgr))
        return pkg_mgr_bom, os_dist

    def run_bdba(self):
        """
        Tar files for BDBA and run the BDBA scan
        """
        self.log_phase("BDBA")
        start_bdba = datetime.now()
        if not self.use_offline_files:
            logging.info(
                "The bdba zip file to scan will be written to {}".format(
                    os.path.join(self.blackduck_output_dir, "bdba_ready.zip")))
        else:
            if os.path.exists(os.path.join(self.blackduck_output_dir, "bdba_ready.zip")):
                logging.info("Attempting to use offline files for BDBA at location: {}".format(
                    os.path.join(self.blackduck_output_dir, 'bdba_ready.zip')))
            else:
                logging.error(
                    "Unable to find previously generated offline files for BDBA..set use_offline_files to false to generate new ones.")
        if not self.offline_mode:
            BDBAApi(self.hub_api).upload_binary(self.hub_project_name,
                                                self.hub_project_vers,
                                                self.codelocation_name,
                                                os.path.join(self.blackduck_output_dir, "bdba_ready.zip"))
        end_bdba = datetime.now()
        logging.info('Time taken to get bdba results: {}'.format(end_bdba - start_bdba))

    def run_sig_scan(self, emit_wrapper_output_sig, os_dist, pkg_mgr_bom_bdba_data=None):
        """
        Download the sig scanner if appropriate, zip files to be scanned, and run the sig scanner
        :param emit_wrapper_output_sig: the files to be tarred and scanned by the sig scanner
        :param os_dist: the current OS
        :param pkg_mgr_bom_bdba_data: a dict of header files to additionally scan
        """
        self.log_phase("BD Signature Scan")
        start_sig = datetime.now()
        sig_scanner = SigScanner(self.cov_home,
                                 self.hub_api,
                                 pkg_mgr_bom_bdba_data,
                                 self.hub_project_name,
                                 self.hub_project_vers,
                                 self.codelocation_name,
                                 emit_wrapper_output_sig,
                                 self.blackduck_output_dir,
                                 self.offline_mode,
                                 self.scan_cli_dir,
                                 self.use_offline_files,
                                 os_dist,
                                 self.additional_sig_scan_args,
                                 self.expand_sig_files,
                                 self.my_args.args.scan_interval,
                                 self.my_args.args.json_splitter_limit,
                                 self.my_args.args.bdio_split_max_file_entries,
                                 self.my_args.args.bdio_split_max_chunk_nodes,
                                 self.my_args.args.disable_bdio_json_splitter,
                                 self.my_args.args.skip_includes,
                                 self.port,
                                 self.verbose)
        sig_scanner.run()
        end_sig = datetime.now()
        logging.info('Time taken to get sig results: {}'.format(end_sig - start_sig))

    def run_bdio_from_package_manager(self):
        """
        Use the results from run_get_package_manager_bom() to create a BDIO file and upload it to Black Duck
        """
        self.log_phase("BDIO from our Package Manager")
        start_bdio = datetime.now()
        bdio2_python_wrapper = BDIO2Transformer(self.blackduck_output_dir, self.hub_api)
        json_file_path = os.path.join(self.blackduck_output_dir, "raw_bdio.json")
        if not os.path.exists(json_file_path):
            logging.warning("The raw BDIO file was not generated. There will not be BDIO results.")
            return
        with open(json_file_path, 'r') as f:
            raw_bdio_json = json.load(f)
        cov_results = [raw_bdio_json]  # Load results from input raw_bdio json
        scan_size = os.stat(json_file_path).st_size  # size of jsonld bdio2 file
        skip_bdio2 = False
        try:
            scanned_path = cov_results[0]['extended-objects'][0]['fullpath'][0]
            if not scanned_path:  # get the scanned path
                scanned_path = "/"
        except IndexError:
            logging.debug(
                "no components present in json {}".format(os.path.join(self.blackduck_output_dir, "raw_bdio.json")))
            skip_bdio2 = True
        if not skip_bdio2:
            result_bdio2_str, code_loc_name = bdio2_python_wrapper.generate_bdio2(self.codelocation_name,
                                                                                  self.hub_project_name,
                                                                                  self.hub_project_vers,
                                                                                  cov_results, scanned_path, scan_size)
            # Rest Remains same above code then code be swapped out once bogdan release his library changes
            bdio2_output_filename = bdio2_python_wrapper.write_bdio2_document(result_bdio2_str)
            logging.info("Created bdio2 file: %s", bdio2_output_filename)
            logging.info("Uploading bdio2 to Black Duck: %s", bdio2_output_filename)
            response = util.upload_scan(bdio2_output_filename, self.hub_api.hub, self.hub_api.bd_url)
            if response.ok:
                print(bdio2_output_filename, "uploaded successfully !!")
            else:
                logging.error("Error uploading {} bdio2 file -- (Response({}): {})".format(bdio2_output_filename,
                                                                                           response.status_code,
                                                                                           response.text))
        end_bdio = datetime.now()
        logging.info('Time taken to get bdio results: {}'.format(end_bdio - start_bdio))

    def final_status(self):
        """
        At the end of the blackduck-c-cpp run, get the status of each phase of the blackduck-c-cpp run and log
        whether it was successful or if it contained errors
        """
        self.log_phase("Blackuck-c-cpp Status Report")
        logging.info("Blackuck-c-cpp run is complete")
        phase_dict = self.get_phase_status_dict()

        phases = phase_dict.keys()
        for item in phases:
            logging.info("Phase {} status: {}".format(item, phase_dict[item]))
        logging.info('Time taken to run: {}'.format(datetime.now() - self.start_time))

    def run_build_capture(self):
        """
        Run each phase of the blackduck-c-cpp process
        """
        os.environ['COVERITY_UNSUPPORTED_COMPILER_INVOCATION'] = "1"
        cov_emit_link_path = ""
        cov_build_run = False
        if self.bazel:
            self.modify_bazel_workspace_file()
        try:
            cov_vers_result = re.search(r"\d+(\.\d+)+", self.cov_version).group().split('.')
        except AttributeError as e:
            # run cov-build when coverity version is not returned
            logging.warning("coverity version is not found - {}, so running cov-build by default".format(self.cov_version))
            cov_build_run = True
        # run cov-build with any version of coverity given
        if self.cov_mode:
            cov_build_run = True
        if not cov_build_run:
            # default mode - runs cov-build when coverity version < 2023.9, else runs cov-cli by default
            if (int(cov_vers_result[0]) >= 2023 and int(cov_vers_result[1]) >= 9) or int(cov_vers_result[0]) >= 2024:
                cov_build_run = None
            else:
                cov_build_run = True

        ## cov-build or cov-cli mode
        if cov_build_run:
            # cov-build mode
            try:
                cov_build_path = glob.glob(os.path.join(self.cov_bin, 'cov-build*'))[0]
                cov_manage_emit_path = glob.glob(os.path.join(self.cov_bin, 'cov-manage-emit*'))[0]
            except IndexError:
                util.error_and_exit(
                    "cov-build or cov-manage-emit not found in bin directory at location: {}".format(self.cov_bin))
        else:
            # defaults to cov-cli mode
            try:
                if platform.system().lower() == 'windows':
                    cov_capture_path = glob.glob(os.path.join(self.cov_bin, 'coverity.exe'))[0]
                else:
                    # correct this to take coverity capture path correctly from the bin directory
                    cov_capture_path = glob.glob(os.path.join(self.cov_bin, 'coverity'))[0]
                cov_manage_emit_path = glob.glob(os.path.join(self.cov_bin, 'cov-manage-emit*'))[0]
            except IndexError:
                util.error_and_exit(
                    "coverity capture or cov-manage-emit or cov-build not found in bin directory at location: {}".format(
                        self.cov_bin))

        try:
            cov_emit_link_path = glob.glob(os.path.join(self.cov_bin, 'cov-emit-link*'))[0]
        except IndexError:
            pass

        # COV BUILD
        if not self.skip_build:
            if self.bld_cmd == '':
                util.error_and_exit("the following argument is required: -bc/--build_cmd")
            #
            if cov_build_run:
                self.run_build(cov_emit_link_path, cov_build_path, cov_build_run)
            else:
                self.run_build(cov_emit_link_path, cov_capture_path, cov_build_run)

        # COV EMIT
        emit_wrapper_output_sig, emit_cov_header_files = self.run_cov_emit()

        # COV EMIT LINK
        if os.path.exists(cov_emit_link_path):
            header_files_set, linker_files_set, executable_files_set = self.run_cov_emit_link(cov_manage_emit_path)
        else:
            logging.info("Not performing coverity json parsing due to absence of cov-emit-link in bin directory")
            header_files_set = linker_files_set = executable_files_set = set()

        # PACKAGE MANAGER BOM
        pkg_mgr_bom, os_dist = self.run_get_package_manager_bom(emit_cov_header_files, header_files_set,
                                                                linker_files_set,
                                                                executable_files_set)

        # BDBA
        if self.BDBA_MODE in self.run_modes or self.ALL_MODE in self.run_modes:
            self.run_bdba()

        # SIG SCAN
        if self.SIG_MODE in self.run_modes or self.ALL_MODE in self.run_modes:
            pkg_mgr_bom_bdba_data = None
            if pkg_mgr_bom:
                pkg_mgr_bom_bdba_data = pkg_mgr_bom.bdba_data
            self.run_sig_scan(emit_wrapper_output_sig, os_dist, pkg_mgr_bom_bdba_data)

        # BDIO
        if not self.offline_mode and (self.PKG_MGR_MODE in self.run_modes or self.ALL_MODE in self.run_modes):
            self.run_bdio_from_package_manager()

        # STATUS
        self.final_status()


def setup_logging(log_path, verbose):
    """
    Set up logging for the module
    """
    format_str = "%(filename)s:%(funcName)s:%(lineno)d:%(asctime)s:%(levelname)s: %(message)s"
    logging.basicConfig(format=format_str, level='DEBUG', filename=log_path, filemode='w')
    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(logging.Formatter(format_str))
    logging.getLogger('').addHandler(console)


def run():
    """
    Entry point
    """
    my_args = C_Parser()
    blackduck_output_dir = my_args.args.output_dir if my_args.args.output_dir else os.path.join(expanduser("~"),
                                                                                                ".blackduck",
                                                                                                "blackduck-c-cpp",
                                                                                                "output",
                                                                                                my_args.args.project_name)

    if not os.path.exists(blackduck_output_dir):
        os.makedirs(blackduck_output_dir)

    log_path = os.path.join(blackduck_output_dir, 'blackduck_c_cpp.log')
    setup_logging(log_path, my_args.args.verbose)

    with RunBuildCapture(my_args, log_path, blackduck_output_dir) as RBC:
        RBC.run_build_capture()


if __name__ == '__main__':
    run()
