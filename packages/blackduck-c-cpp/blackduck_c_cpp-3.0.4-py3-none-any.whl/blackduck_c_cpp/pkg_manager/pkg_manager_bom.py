"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""
import asyncio
import os
import tqdm
import logging
import pandas as pd
import re
import shutil
import csv
import json
import ast
from blackduck_c_cpp.util.build_log_parser import LogParser
from blackduck_c_cpp.pkg_manager.ld_debug_parse import LdDebugParser
from collections import defaultdict
import hashlib
import sys
import itertools
import subprocess
from blackduck_c_cpp.util import global_settings
from blackduck_c_cpp.util import util
from datetime import datetime
import concurrent.futures
import hashlib
from itertools import islice
from pathlib import Path

PKG_MGR_MODE = 'pkg_mgr'
BDBA_MODE = 'bdba'
ALL_MODE = 'all'


class PkgManagerBom:
    """
    Runs package manager on all linker,header,executable and transitive dependency files
    and creates a zip file to send to bdba
    """

    def __init__(self, pkg_manager, build_log, cov_home, blackduck_output_dir, os_dist, bld_dir, unresolved_files_list,
                 resolved_files_list, binary_files_list, json_grep_files_list, skip_build, skip_transitives,
                 skip_dynamic, run_modes,
                 cov_header_files, debug, header_files_set, linker_files_set, executable_files_set,
                 resolved_cov_files_list, unresolved_cov_files_list,
                 hub_api, offline, use_offline_files):
        self.pkg_manager = pkg_manager
        self.build_log = build_log
        self.skip_build = skip_build
        self.skip_transitives = skip_transitives
        self.skip_dynamic = skip_dynamic
        self.output_dir = blackduck_output_dir
        self.cov_home = cov_home
        self.header_list = cov_header_files
        self.bld_dir = bld_dir
        self.os_dist = os_dist
        self.resolved_files_path = resolved_files_list
        self.unresolved_files_path = unresolved_files_list
        self.run_modes = run_modes

        self.resolved_cov_files_path = resolved_cov_files_list
        self.unresolved_cov_files_path = unresolved_cov_files_list

        self.binary_files_path = binary_files_list
        self.json_grep_files_list = json_grep_files_list
        self.debug = debug
        self.cov_header_files_set = header_files_set
        self.cov_linker_files_set = linker_files_set
        self.cov_executable_files_set = executable_files_set
        self.hub_api = hub_api
        self.offline = offline
        self.use_offline_files = use_offline_files

        self.csv_file_path = os.path.join(self.output_dir, "raw_bdio.csv")
        self.json_file_path = os.path.join(self.output_dir, "raw_bdio.json")
        self.executable_list = None
        self.linker_list = None
        self.lib_path_set = None
        self.build_dir_dict = None
        self.components_data = None
        self.final_components_dict = None
        self.file_dict = dict()
        self.resolved_file_dict = dict()
        self.unresolved_file_dict = dict()
        self.cov_file_dict = dict()
        self.resolved_cov_file_dict = dict()
        self.unresolved_cov_file_dict = dict()
        self.pkg_mgr_data = dict()
        self.bdba_data = dict()
        self.ldd_linker = dict()
        self.lddebug_executable = dict()
        self.unrecognized_pkg_manager = True
        self.direct_match_evidence = 'Binary'
        self.transitive_match_evidence = 'Binary'
        self.unresol_set = set()
        self.BATCH_SIZE = 100
        self.dups_count = 0
        self.seen_files_for_pkg_mgr = dict()

        self.parse_logic_patterns = {
            "file": re.compile(r"(?<=file:)([^ ])*"),
            "pkg": re.compile(r"(?<=pkg:)([^ ])*"),
            "version": re.compile(r"(?<=version:)([^ ])*"),
            "confidence": re.compile(r"(?<=confidence:)([^ ])*"),
            "size": re.compile(r"(?<=size:)([^ ])*"),
            "timestamp": re.compile(r"(?<=timestamp:)([^ ])*"),
            "sha1": re.compile(r"(?<=sha1sum:)([^ ])*"),
            "matchtype": re.compile(r"(?<=matchType:)([^ ])*"),
            "arch": re.compile(r"(?<=package-architecture:)([^ ])*"),
            "epoch": re.compile(r"(?<=epoch:)([^ ])*"),
            "release": re.compile(r"(?<=release:)([^ ])*"),
            "remove_parentheses": re.compile(r"[()]"),
        }

    def run_log_parser(self):
        """
        This function calls LogParser.parse_build_log method to get all paths from linker invocations,
        all output executables and -L paths from build_log.txt for path resolution

        """
        start_parser = datetime.now()
        log_parser = LogParser()
        self.linker_list = log_parser.parse_build_log(self.build_log, self.os_dist)
        self.lib_path_set = log_parser.lib_path
        self.executable_list = log_parser.get_exectuable(self.build_log)
        end_parser = datetime.now()
        logging.info("time taken to parse for files from build-log.txt : {}".format(end_parser - start_parser))

    def get_files(self, list_paths):
        """
        Function to create a dictionary with input list of paths in sorted order with length
        {a.so: [g/b/c/a.so,c/a.so],...}
        param: list of paths
        return: dictionary containing key as basefile and value as list of all paths with basefile
        """
        basefile_list = list(map(lambda path: os.path.basename(path).strip(), list_paths))
        basefiles_dict = dict.fromkeys(basefile_list, None)
        for basefile in basefiles_dict.keys():
            basefiles_dict[basefile] = sorted(
                set(map(lambda path_1: path_1.strip(),
                        filter(lambda path: os.path.basename(path).endswith(basefile), list_paths))),
                key=len,
                reverse=True)
        return basefiles_dict

    def generate_build_dir_files(self):
        """ This function gets all files in build dir
        return: dictionary containing key as basefile and value as list of all paths with basefile in build directory
        """
        start_gen = datetime.now()
        basefiles_dict = dict()
        dirs_set = set()
        count = 0
        for (root, dirs, files) in os.walk(self.bld_dir, followlinks=True):
            logging.debug("root is {}".format(root))
            st = os.stat(root)
            walk_dirs = []
            for dirname in dirs:
                st = os.stat(os.path.join(root, dirname))
                dir_key = st.st_dev, st.st_ino
                if dir_key not in dirs_set:
                    dirs_set.add(dir_key)
                    walk_dirs.append(dirname)
            for file in files:
                if file in self.unresol_set:
                    if file in basefiles_dict:
                        basefiles_dict[file] = basefiles_dict[file] + [os.path.join(root, file)]
                    else:
                        basefiles_dict[file] = [os.path.join(root, file)]
                    count += 1
                    if (count % 1000 == 0):
                        logging.debug("files resolved so far {}".format(len(basefiles_dict.keys())))
            dirs[:] = walk_dirs
        end_gen = datetime.now()
        logging.debug("total list of files found are : {}".format(len(basefiles_dict.keys())))
        logging.debug("time taken to get all files in build dir : {}".format(end_gen - start_gen))
        return basefiles_dict

    def test_for_dash_l_file_completion(self, path_list):
        """ This function will attempt to resolve paths to files based on paths found
        as -L flags in the build-log
        param: list of paths
        return: set of resolved paths with length used for sort in descending order
        """
        resolved_paths = set()
        for path in path_list:
            if os.path.exists(path):
                resolved_paths.add(path)
            else:
                for lib_path in self.lib_path_set:
                    test_path = os.path.abspath(util.resolve_path(os.path.join(lib_path, path)))
                    if os.path.exists(test_path):
                        resolved_paths.add(test_path)
                        break
        return sorted(resolved_paths, key=len, reverse=True)

    def resolve_file_paths(self, basefiles_dict):
        """ This function separates all files to resolved and unresolved files
        param: dictionary containing key as basefile and value as list of all paths with basefile
        return: resolved and unresolved dictionaries with key as basefile and value as list of all paths with basefile
        """
        resolved_files_dict = dict()
        unresolved_files_dict = dict()
        for basefile, paths_list in basefiles_dict.items():
            resolved_paths = self.test_for_dash_l_file_completion(paths_list)
            if len(resolved_paths) > 0:
                resolved_files_dict[basefile] = set(resolved_paths)
            else:
                try:
                    """looks in build directory files"""
                    if basefile in self.build_dir_dict:
                        resolved_files_dict[basefile] = set(self.build_dir_dict[basefile])
                    else:
                        """ add to unresolved dictionary only if not even a single path in paths_list is resolved"""
                        unresolved_files_dict[basefile] = set(paths_list)
                except IndexError:
                    continue
        return resolved_files_dict, unresolved_files_dict

    def write_to_txt(self, input_dict, path):
        """This function is used to write resolved files, unresolved files and all files to text files
        param: dictionary to write to a file
        """
        try:
            with open(path, "w") as file_wr:
                file_wr.write("{\n")
                for type in input_dict.keys():
                    file_wr.write("'For {}:'\n".format(type))
                    for basefile in input_dict[type].keys():
                        file_wr.write("'{}':'{}'\n".format(basefile, input_dict[type][basefile]))
                        file_wr.write("\n")
                file_wr.write("}")
        except OSError:
            logging.error("Couldn't write file: {}".format(path))

    def join_components(self, sha1, confidence, pkg_result, matchType):
        """ This function joins sha1,confidence and package manager result with matchType to return a single string
        param:
            sha1: string
            confidence: string
            pkg_result: string
            matchType: string
        return: string
        """
        matchType = "matchType:{}".format(matchType)
        pkg_result = " ".join([pkg_result, sha1])
        pkg_result = " ".join([pkg_result, confidence])
        pkg_result = " ".join([pkg_result, matchType])
        return pkg_result


    async def pkg_mgr_batch_process(self, batch_list):
        pattern_file = global_settings.pattern_file
        pkg_dict = {}
        bdba_dict = {}
        if self.pkg_manager in ['rpm', 'dpkg']:
            self.unrecognized_pkg_manager = False
        MatchType = self.direct_match_evidence
        batch_dict = dict(batch_list)

        tasks = []
        for basefile, paths_list in batch_dict.items():
            if isinstance(paths_list, set):
                paths_list = list(paths_list)
            tasks.append(self.run_pkg_query(paths_list))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result, (basefile, paths_list) in zip(results, batch_dict.items()):
            if isinstance(result, Exception) and self.os_dist != 'windows':
                logging.debug(f"Error processing {basefile}: {result}")
                bdba_dict[basefile] = paths_list
            else:
                sha1, confidence, pkg_result, success = result
                if success:
                    pkg_result = self.join_components(sha1, confidence, pkg_result, MatchType)
                    file_path = re.search(pattern_file, pkg_result).group()
                    pkg_dict[file_path] = pkg_result
                    if self.debug or self.unrecognized_pkg_manager:
                        bdba_dict[basefile] = paths_list
                else:
                    bdba_dict[basefile] = paths_list
        return pkg_dict, bdba_dict


    async def check_pkg_mgr(self, basefiles_dict):
        """ This function sends files to package manager and if no result adds those files to bdba
        param: dictionary containing key as basefile and value as list of all paths with basefile
        return: package manager dicitonary with key as filepath and value as result of package manager
                bdba dicitonary with key as basefile and value as list of all paths with basefile
        """
        pkg_joined_results = {}
        bdba_joined_results = {}

        # Dynamically calculate optimal batch size
        max_batch_size = self.BATCH_SIZE
        num_items = len(basefiles_dict)
        batch_size = min(max_batch_size, max(1, num_items // (os.cpu_count() or 10)))

        batches = [list(basefiles_dict.items())[i:i+batch_size] for i in range(0, num_items, batch_size)]

        tasks = [self.pkg_mgr_batch_process(batch) for batch in batches]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logging.debug(f"Error in batch processing: {result}")
            else:
                pkg_result, bdba_result = result
                pkg_joined_results.update(pkg_result)
                bdba_joined_results.update(bdba_result)

        return pkg_joined_results, bdba_joined_results

    async def run_pkg_query(self, paths_list):
        """ This function calls respective package manager function
        param: list of paths
        return: returns package manager result if exists otherwise returns "error"
            sha1: string
            confidence: string
            pkg_result: string
            result: Boolean
        """
        if self.pkg_manager == "dpkg":
            sha1, confidence, pkg_result, result = await self.run_dpkg_command_batch(paths_list)
        elif self.pkg_manager == "rpm":
            sha1, confidence, pkg_result, result = await self.run_rpm_command_batch(paths_list)
        elif self.pkg_manager == "brew":
            sha1, confidence, pkg_result, result = await self.run_brew_command_batch(paths_list)
        else:
            sha1, confidence, pkg_result, result = self.run_generic_command_batch(paths_list)

        return sha1, confidence, pkg_result, result

    async def run_dpkg_command_batch(self, paths_list):
        """ This function runs dpkg package manager command
        param: list of paths
        return: sha1,confidence and package result - all params in string format
        """
        result = False
        for path in paths_list:
            sha1, confidence, pkg_result = await self._run_dpkg_query(path)
            if ("\n" not in pkg_result) and ("error" not in pkg_result):
                result = True
                return sha1, confidence, pkg_result, result
            else:
                path_obj = Path(path)
                if path_obj.is_symlink():
                    orig_path = str(path_obj.resolve())
                    sha1, confidence, pkg_result = await self._run_dpkg_query(orig_path)
                    if ("\n" not in pkg_result) and ("error" not in pkg_result):
                        result = True
                        return sha1, confidence, pkg_result, result
        return "error", "error", "error", result


    async def _run_dpkg_query(self, path):
        """ This function runs dpkg package manager command
        param: list of paths
        return: sha1,confidence and package result - all params in string format
        """
        dpkg_command = (
            f"dpkg-query --showformat='file:{path} src:${{Source}} pkg:${{Package}} "
            f"version:${{Version}} package-architecture:${{Architecture}} "
            f"timestamp:${{db-fsys:Last-Modified}} size:${{Installed-Size}}\\n' "
            f"--show `dpkg -S {path} | awk -F: '{{print $1}}'`"
        )
        process = await asyncio.create_subprocess_shell(
            dpkg_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0 and (("dpkg: error:" not in stdout.decode()) and ("no path found matching" not in stdout.decode())):
            sha1 = self.find_sha1sum(path)
            confidence = "confidence:100"
            dpkg_result = stdout.decode().strip()
            return sha1, confidence, dpkg_result
        else:
            return "error", "error", "error"

    async def run_rpm_command_batch(self, paths_list):
        """ This function runs rpm package manager command
        param: list of paths
        return: sha1,confidence and package result - all params in string format
        """

        result = False
        for path in paths_list:
            sha1, confidence, pkg_result = await self._run_rpm_query(path)
            if ("\n" not in pkg_result) and ("error" not in pkg_result):
                result = True
                return sha1, confidence, pkg_result, result
            else:
                path_obj = Path(path)
                if path_obj.is_symlink():
                    orig_path = str(path_obj.resolve())
                    sha1, confidence, pkg_result = await self._run_rpm_query(orig_path)
                    if ("\n" not in pkg_result) and ("error" not in pkg_result):
                        result = True
                        return sha1, confidence, pkg_result, result
        return "error", "error", "error", result

    async def _run_rpm_query(self, path):
        """
        Run a single rpm command asynchronously.
        """
        rpm_command = (
            f"rpm -q --queryformat 'file:{path} src:%{{SOURCERPM}} pkg:%{{Name}} "
            f"version:%{{Version}} package-architecture:/%{{ARCH}} timestamp:%{{FILEMTIMES}} "
            f"size:%{{FILESIZES}} epoch:%{{EPOCH}}: release:-%{{RELEASE}}\\n' --whatprovides {path}"
        )
        process = await asyncio.create_subprocess_shell(
            rpm_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0 and "error" not in stdout.decode():
            sha1 = self.find_sha1sum(path)
            confidence = "confidence:100"
            rpm_result = stdout.decode().strip()
            return sha1, confidence, rpm_result
        return "error", "error", "error"

    async def run_brew_command_batch(self, paths_list):
        """ This function runs brew package manager command
        param: list of paths
        return: sha1,confidence and package result - all params in string format
        """
        result = False
        for path in paths_list:
            sha1, confidence, pkg_result = await self._run_brew_query(path)
            if ("\n" not in pkg_result) and ("error" not in pkg_result):
                result = True
                return sha1, confidence, pkg_result, result
            else:
                path_obj = Path(path)
                if path_obj.is_symlink():
                    orig_path = str(path_obj.resolve())
                    sha1, confidence, pkg_result = await self._run_brew_query(orig_path)
                    if ("\n" not in pkg_result) and ("error" not in pkg_result):
                        result = True
                        return sha1, confidence, pkg_result, result
        return "error", "error", "error", result

    async def _run_brew_query(self, path):
        """
        Run a single brew command asynchronously.
        """
        sha1, confidence, brew_result = "error", "error", "error"
        match_type = self.direct_match_evidence
        match_type = f"matchType:{match_type}"

        if "Cellar" in path:
            path_split = path.split('/')
            try:
                pkg_result = f"file:{path} pkg:{path_split[4].split('@')[0]} version:{path_split[5]}"
                sha1 = self.find_sha1sum(path)
                confidence = "confidence:100"
                size = "size:0"
                timestamp = "timestamp:111"
                package_architecture = "package-architecture:none"
                brew_result = " ".join([pkg_result, timestamp, size, package_architecture, match_type])
                return sha1, confidence, brew_result
            except IndexError:
                pass
        return sha1, confidence, brew_result

    def run_windows_command(self, paths_list):
        """ This function runs for windows or when package manager and os_dist is not found
        """
        return "error", "error", "error"

    def run_generic_command_batch(self, paths_list):
        """when package manager or os_dist is not found
        """
        return "error", "error", "error"



    async def check_ldd(self, basefiles_dict):
        """
        This function calls ldd for all .so files in batches using the optimized batch function.
        param: dictionary containing key as basefile and value as list of all paths with basefile
        return: dictionary with key as filepath and
                value as dictionary with key transitive dependency element and value package manager results for it
        """
        ldd_linker = {}
        bdba_dict = {}

        # Collect all .so file paths
        so_filepaths = [
            filepath
            for filepath, _ in basefiles_dict.items()
            if re.match(r".*\.so$|.*\.so\..+$", filepath)
        ]

        # Use the batch function to get ldd results
        ldd_results = await self.get_ldd_for_sharedlib_batch(so_filepaths)
        if ldd_results is None:
            logging.debug("get_ldd_for_sharedlib_batch returned None")
            ldd_results = {}
        # Process the results
        max_batch_size = self.BATCH_SIZE
        num_items = len(ldd_results)
        batch_size = min(max_batch_size, max(1, num_items // (os.cpu_count() or 1)))

        def batch_iterable(iterable, batch_size):
            """Helper function to split an iterable into batches."""
            it = iter(iterable)
            while batch := list(islice(it, batch_size)):
                yield batch

        for batch in batch_iterable(ldd_results.items(), batch_size):
            tasks = [
                self.check_pkg_for_ldds(dependencies, bdba_dict)
                for filepath, dependencies in batch
                if dependencies
            ]
            dep_dicts = await asyncio.gather(*tasks, return_exceptions=True)

            for (filepath, dependencies), dep_dict in zip(batch, dep_dicts):
                if isinstance(dep_dict, Exception):
                    logging.debug(f"Error processing {filepath}: {dep_dict}")
                else:
                    ldd_linker[filepath] = dep_dict

        return ldd_linker, bdba_dict


    async def check_pkg_for_ldds(self, ldd_list, bdba_dict):
        """
        This function calls the package manager for ldds in batches.
        param: ldd_list - list of transitive dependencies for each .so file
        param: bdba_dict - dictionary to store unresolved dependencies
        return: dictionary with key as transitive dependency element and value as package manager result for it
        """
        match_type = self.transitive_match_evidence
        ldd_dict = dict()

        tasks = [
            self._process_ldd_element(ldd_ele.strip(), match_type)
            for ldd_ele in ldd_list
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for ldd_ele, pkg_result in zip(ldd_list, results):
            if isinstance(pkg_result, Exception) or pkg_result == {}:
                logging.debug(f"Error or empty result processing {ldd_ele}: {pkg_result}")
                bdba_dict[os.path.basename(ldd_ele)] = set([ldd_ele])
            else:
                ldd_dict.update(pkg_result)
                if self.debug:
                    bdba_dict[os.path.basename(ldd_ele)] = set([ldd_ele])
        return ldd_dict


    async def _process_ldd_element(self, ldd_ele, match_type):
        """
        Helper function to process a single ldd element.
        param: ldd_ele - a single transitive dependency
        param: match_type - match type for the dependency
        return: dictionary with the ldd element as key and package manager result as value
        """
        # # check if result is already in seen_files_for_pkg_mgr
        if ldd_ele in self.seen_files_for_pkg_mgr:
            self.dups_count +=1
            return {ldd_ele: self.seen_files_for_pkg_mgr[ldd_ele]}
        # if not in seen_files_for_pkg_mgr, run the package manager query
        sha1, confidence, pkg_result, result = await self.run_pkg_query(
            [ldd_ele, os.path.basename(ldd_ele)]
        )
        if result:
            pkg_result = self.join_components(sha1, confidence, pkg_result, match_type)
            return {ldd_ele: pkg_result}
        else:
            return {}

    async def get_ldd_for_sharedlib_batch(self, so_filepaths):
        """
        Optimized function to call ldd parse function on multiple .so files in batches.
        param: so_filepaths - list of .so file paths
        return: dictionary with file path as key and list of transitive dependencies as value
        """
        results = {}

        # Dynamically calculate batch size based on CPU cores
        max_batch_size = 100  # Define a reasonable upper limit for batch size
        num_paths = len(so_filepaths)
        batch_size = min(max_batch_size, max(1, num_paths // (os.cpu_count() or 1)))

        for i in range(0, num_paths, batch_size):
            batch = so_filepaths[i:i + batch_size]
            tasks = [self._ldd_output_parse(filepath) for filepath in batch if os.path.exists(filepath)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for filepath, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logging.debug(f"Error processing {filepath}: {result}")
                    results[filepath] = []
                else:
                    results[filepath] = result

        return results

    async def _ldd_output_parse(self, full_path):
        """
        Helper function to perform parsing on the output of the ldd command for a single file.
        param: full_path - .so file path
        return: list of distinct transitive dependencies
        """
        try:
            process = await asyncio.create_subprocess_shell(
                f"ldd {full_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                parsed_results = re.findall(r'^\s*(\S+)\s+=>(.*) \(.*\)$', stdout.decode(), re.MULTILINE)
                return [path.strip() for _, path in parsed_results if path.strip()]
            else:
                logging.debug(f"ldd command failed for {full_path}: {stderr.decode().strip()}")
                return []
        except Exception as e:
            logging.debug(f"Exception while running ldd for {full_path}: {e}")
            return []

    def find_sha1sum(self, path):
        """This function finds sha1 of a file
        param: filepath - string
        return: sha1 - string
        """
        sha1 = hashlib.sha1()
        try:
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    sha1.update(chunk)
            return "sha1sum:{}".format(sha1.hexdigest())
        except Exception:
            return "sha1sum:notAvailable"


    def can_perform_ldd(self):
        """This function checks if ldd is present in the system"""
        return shutil.which('ldd') is not None

    async def check_ldd_deb(self, executables):
        """This function calls ld debug function on executables
        param: dictionary of executables - key: executable basefile, value: list of paths
        return: dictionary with key: direct dependency,
        value: dictionary with key transitive dependency element and value as package manager result for it
        """
        ld = LdDebugParser()
        ld_deb_dict = dict()
        ld_return_dict = dict()
        bdba_dict = dict()
        for executable, exec_list in executables.items():
            for each_ele in exec_list:
                str_ele = each_ele.strip(" ").strip('\"')
                ld_debug_dict = ld.run_ld_debug(str_ele, self.bld_dir)
                ld_deb_dict[str_ele] = ld_debug_dict
        for executable, components in ld_deb_dict.items():
            for dependency, dependency_of_dep in components.items():
                ld_return_dict[dependency] = await self.check_pkg_for_ldds(list(dependency_of_dep),bdba_dict)
        return ld_return_dict, bdba_dict

    async def check_components(self):
        """This function creates final dictionary joining all direct (from linker and header)
        and transitive dependencies from ldd and ld_debug
        """
        pkg_mgr_components = {**self.pkg_mgr_data['linker'], **self.pkg_mgr_data['header']}
        linker_components = self.ldd_linker
        ld_debug_components = self.lddebug_executable
        left_ovr_pairs_linker = set(linker_components.keys())
        left_ovr_pairs_ld_debug = set(ld_debug_components.keys())

        trans_dep_dict = defaultdict(set)
        for each_component, pkg_result in pkg_mgr_components.items():

            if each_component in linker_components:
                for dep_1, ldd_pkg_mgr_res in linker_components[each_component].items():
                    trans_dep_dict[pkg_result].add(ldd_pkg_mgr_res)
                left_ovr_pairs_linker.remove(each_component)

            if each_component in ld_debug_components:
                for dep_2, ld_pkg_mgr_res in ld_debug_components[each_component].items():
                    trans_dep_dict[pkg_result].add(ld_pkg_mgr_res)
                left_ovr_pairs_ld_debug.remove(each_component)

            if (each_component not in linker_components) and (each_component not in ld_debug_components):
                trans_dep_dict[pkg_result] = set()

        sub_linker_components = {key: linker_components[key] for key in left_ovr_pairs_linker if
                                 key in linker_components}
        sub_ld_debug_components = {key: ld_debug_components[key] for key in left_ovr_pairs_ld_debug if
                                   key in ld_debug_components}

        logging.debug("sub_linker_components is {}".format(sub_linker_components))
        logging.debug("sub_ld_debug_components is {}".format(sub_ld_debug_components))

        for dep, dep_trans in sub_linker_components.items():
            sha1, confidence, pkg_result_1, result = await self.run_pkg_query([dep])
            if result:
                pkg_result_1 = self.join_components(sha1, confidence, pkg_result_1, self.direct_match_evidence)
                for dep_3, ld_pkg_mgr_r in dep_trans.items():
                    trans_dep_dict[pkg_result_1].add(ld_pkg_mgr_r)

        for dep, dep_trans in sub_ld_debug_components.items():
            sha1, confidence, pkg_result_1, result = await self.run_pkg_query([dep])
            if result:
                pkg_result_1 = self.join_components(sha1, confidence, pkg_result_1, self.direct_match_evidence)
                for dep_3, ld_pkg_mgr_r in dep_trans.items():
                    trans_dep_dict[pkg_result_1].add(ld_pkg_mgr_r)
        return trans_dep_dict

    def create_csv(self, table_df):
        """This function creates raw_bdio.csv"""
        self.csv_fields_size()
        if table_df != []:
            if self.pkg_manager == 'rpm':
                df = pd.DataFrame(table_df,
                                  columns=["distro", "fullpath", "package-name", "package-version", "confidence",
                                           "size",
                                           "timestamp", "sha1", "matchType", "package-architecture", "epoch", "release",
                                           "trans-dep"])

            elif self.pkg_manager == 'dpkg':
                df = pd.DataFrame(table_df,
                                  columns=["distro", "fullpath", "package-name", "package-version", "confidence",
                                           "size",
                                           "timestamp", "sha1", "matchType", "package-architecture", "trans-dep"])
            elif self.pkg_manager == 'brew':
                df = pd.DataFrame(table_df,
                                  columns=["distro", "fullpath", "package-name", "package-version", "confidence",
                                           "size",
                                           "timestamp", "sha1", "matchType", "trans-dep"])
                df['package-architecture'] = 'none'
            df['separator'] = '/'
            df['package-type'] = self.pkg_manager
            df['type'] = 'distro-package'
            # csv_file_short = os.path.join(self.output_dir, "raw_bdio_short.csv")
            df[["size", "timestamp", "confidence"]] = df[["size", "timestamp", "confidence"]].apply(pd.to_numeric,
                                                                                                    errors='coerce')
            df[["size", "timestamp", "confidence"]] = df[["size", "timestamp", "confidence"]].fillna(value=0)
            df[["size", "timestamp", "confidence"]] = df[["size", "timestamp", "confidence"]].astype(int)
            df.fullpath = df.fullpath.apply(lambda x: tuple(x) if type(x) != str else tuple([x]))
            logging.debug("length of dataframe is {}".format(len(df)))
            df1 = df.groupby(
                ["package-name", "package-version", "package-architecture"]).agg({'trans-dep': sum}).reset_index()
            df1 = pd.merge(df1, df[
                ["distro", "fullpath", "package-name", "package-version", "package-architecture", "confidence", "size",
                 "timestamp", "sha1",
                 "matchType", "type", "package-type"]], on=["package-name", "package-version", "package-architecture"],
                           how='inner')
            df1['trans-dep'] = df['trans-dep'].apply(
                lambda x: [list(tdep_t) for tdep_t in set(tuple(tdep) for tdep in x)])
            duplicate_res = df1['trans-dep'].astype(str).duplicated()
            df1['trans-dep'] = df1['trans-dep'].where(~duplicate_res, "[]")
            df1['trans-dep'] = df1['trans-dep'].astype(str)
            df1['length'] = df1['trans-dep'].str.len()
            logging.debug("df1 columns are {}".format(df1.columns))
            df1.sort_values('length', ascending=False, inplace=True)
            df1.to_csv(self.csv_file_path,
                       columns=["distro", "fullpath", "package-name", "package-version", "package-architecture",
                                "confidence",
                                "size", "timestamp", "sha1", "matchType", "type", "package-type", "trans-dep"],
                       index=False)
            logging.info("raw_bdio.csv written to location {}".format(self.output_dir))
        else:
            df1 = pd.DataFrame(columns=["distro", "fullpath", "package-name", "package-version", "package-architecture",
                                        "confidence",
                                        "size", "timestamp", "sha1", "matchType", "type", "package-type", "trans-dep"])
            df1.to_csv(self.csv_file_path, index=False)
            logging.warning("Empty csv written..no package manager result found")

    def parse_components_info(self):
        """function to parse package manager result string into list of values"""
        table_df = []
        for component, trans_components_set in self.final_components_dict.items():
            col_df = self.parse_logic(component)

            trans_list = [
                self.parse_logic(each_trans_comp, trans_status=True)
                for each_trans_comp in trans_components_set
            ]

            uniq_trans_list = list(_trans_list for _trans_list, _ in itertools.groupby(sorted(trans_list)))

            col_df.append(uniq_trans_list)
            table_df.append(col_df)
        self.create_csv(table_df)

    def parse_logic(self, component_str, trans_status=False):
        """ parsing logic for package manager result string
        param: string - package manager result
        return: list
        for eg: ['a/b/c.so','openssl','1.2.3',100,12436,2425364646,'faa816df1c632fcba5c4d525a180aa4c8b85f515',...]
        """
        component_info = []
        """ If os distribtion is mac/windows, setting it to fedora to get more external id matches """
        if self.os_dist == "Mac" or self.os_dist == "windows":
            self.os_dist = "fedora"
        component_info.append(self.os_dist)
        patterns = self.parse_logic_patterns

        fullpath_info = (self.bld_dir, re.search(patterns["file"], component_str).group() if re.search(patterns["file"],
                                                                                                       component_str) else "unknown")
        pkg_info = re.search(patterns["pkg"], component_str).group() if re.search(patterns["pkg"],
                                                                                  component_str) else "unknown"
        pkg_version_info = re.search(patterns["version"], component_str).group() if re.search(patterns["version"],
                                                                                              component_str) else "unknown"

        try:
            confidence_info = int(re.search(patterns["confidence"], component_str).group())
        except (ValueError, AttributeError):
            confidence_info = 0

        try:
            size_match = re.search(patterns["size"], component_str)
            size_info = int(size_match.group().strip()) if size_match and size_match.group().strip().isdigit() else 0
        except (ValueError, AttributeError):
            size_info = 0

        try:
            time_info = int(re.search(patterns["timestamp"], component_str).group())
        except (ValueError, AttributeError):
            time_info = 0

        try:
            time_info = int(re.search(patterns["timestamp"], component_str).group())
        except (ValueError, AttributeError):
            time_info = 0

        sha1_info = re.search(patterns["sha1"], component_str).group() if re.search(patterns["sha1"],
                                                                                    component_str) else "sha1sum:notAvailable"
        matchtype_info = re.search(patterns["matchtype"], component_str).group() if re.search(patterns["matchtype"],
                                                                                              component_str) else "unknown"

        if self.pkg_manager != 'brew':
            architecture_info = re.sub(patterns["remove_parentheses"], "",
                                       re.search(patterns["arch"], component_str).group()) if re.search(
                patterns["arch"], component_str) else "unknown"
        if self.pkg_manager == 'rpm':
            epoch_info = re.sub(patterns["remove_parentheses"], "",
                                re.search(patterns["epoch"], component_str).group()) if re.search(patterns["epoch"],
                                                                                                  component_str) else "none"
            release_info = re.sub(patterns["remove_parentheses"], "",
                                  re.search(patterns["release"], component_str).group()) if re.search(
                patterns["release"], component_str) else "none"
            pkg_version_info = epoch_info.replace("none:", "") + pkg_version_info + release_info.replace("-none", "")
            architecture_info = architecture_info.strip("/") if 'architecture_info' in locals() else "unknown"

        component_info.extend([
            fullpath_info, pkg_info, pkg_version_info, confidence_info, size_info, time_info, sha1_info
        ])

        if trans_status:
            component_info.append('distro-package')
        component_info.append(matchtype_info)
        if self.pkg_manager != 'brew':
            component_info.append(architecture_info)
        if self.pkg_manager == 'rpm':
            component_info.extend([epoch_info, release_info])
        return component_info

    def trans_key_value(self, string_in):
        """ function to append keys for transitive dependency list from csv for json
        param: string - package manager result for transitive dependency
        return: list of dictionaries
        eg: [{'distro':'ubuntu',..'package-name':'curl'..},
         {'distro':'ubuntu',..'package-name':'gcc'..}..]
        """
        dict_keys = ['distro', 'fullpath', 'package-name', 'package-version', 'confidence', 'size', 'timestamp', 'sha1',
                     'type',
                     'matchType', 'package-architecture']
        trans_dep_list = []
        list_in = ast.literal_eval(string_in)
        for each_list in list_in:
            if each_list != "[]":
                trans_dep_dict = dict(zip(dict_keys, each_list))
                trans_dep_list.append(trans_dep_dict)
        return trans_dep_list

    def csv_to_json(self):
        """This function converts raw_bdio.csv to raw_bdio.json"""
        data = {}
        try:
            with open(self.csv_file_path, encoding=util.get_encoding(self.csv_file_path), errors='replace') as csvf:
                csvReader = csv.DictReader(csvf)
                key1 = 'extended-objects'
                data['extended-objects'] = []
                for rows in csvReader:
                    new_row = dict()
                    for key, value in rows.items():
                        if key == 'trans-dep':
                            if value != "[]":
                                trans_dep_list = self.trans_key_value(value)
                                new_row[key] = trans_dep_list
                        elif key != 'fullpath':
                            try:
                                new_row[key] = int(value)
                            except ValueError:
                                new_row[key] = value
                        else:
                            new_row[key] = ast.literal_eval(value)
                    data[key1].append(new_row)
            try:
                with open(self.json_file_path, 'w', encoding=util.get_encoding(self.json_file_path), errors='replace') as jsonf:
                    jsonf.write(json.dumps(data, indent=4))
                logging.info("raw_bdio.json written to location {}".format(self.output_dir))
            except OSError:
                logging.error("Couldn't write file {}".format(self.json_file_path))
        except FileNotFoundError:
            logging.error("raw_bdio.csv file not found - make sure csv file is written correctly")

    ## zip file
    def zip_files(self):
        """this function zip file for bdba"""
        zip_set_files = set()
        # [[[zip_set_files.add(path) for path in paths] for paths in type.values()] for type in self.bdba_data.values()]
        for type in {type: val for type, val in self.bdba_data.items() if type != 'header'}.values():
            for paths in type.values():
                for path in paths:
                    zip_set_files.add(path)

        logging.info("\nZipping all binary files\n")
        dir_path = os.path.join(self.output_dir, "bdba_ready.zip")
        util.zip_files(zip_set_files, dir_path)
        logging.info("Files are placed in '{}' ".format(self.output_dir))
        logging.info("Number of files in bdba zip file are {}".format(len(zip_set_files)))

    def csv_fields_size(self):
        max_int = sys.maxsize
        while True:
            # decrease the maxInt value by factor 10  as long as the OverflowError occurs.
            try:
                csv.field_size_limit(max_int)
                break
            except OverflowError:
                max_int = int(max_int / 10)

    def get_dict_difference(self, json_dict, grep_dict):
        """ function to get files present in json and not in grep and vice versa
        param: json_dict: key with basefile, value as list of paths with that file from coverity json
               grep_dict: key with basefile, value as list of paths with that file from grep
        return: dict_json : files present in json not present in grep as dictionary with key as basefile and value as list of paths
                dict_grep : files present in grep not present in json as dictionary with key as basefile and value as list of paths
        """
        json_keys = set(json_dict.keys())
        # logging.debug("json keys are {}".format(json_keys))
        grep_keys = set(grep_dict.keys())
        # logging.debug("grep keys are {}".format(grep_keys))
        other_keys_in_json = json_keys - grep_keys
        other_keys_in_grep = grep_keys - json_keys
        dict_json = dict((key, json_dict[key]) for key in other_keys_in_json)
        dict_grep = dict((key, grep_dict[key]) for key in other_keys_in_grep)
        return dict_json, dict_grep

    def join_json_grep(self, json_dict, file_type):
        """ function to append resolved coverity json paths which were not found by grep to resolved_file_dict
        param: json_dict: key with basefile, value as list of paths with that file from coverity json
               file_type: 'header', 'linker' or 'executable'
        """
        # adding the values with common key
        for key in json_dict:
            if key in self.resolved_file_dict[file_type]:
                # logging.debug("self.resolved_file_dict[file_type][key] is {}".format(self.resolved_file_dict[file_type][key]))
                self.resolved_file_dict[file_type][key].union(json_dict[key])
            else:
                self.resolved_file_dict[file_type][key] = set(json_dict[key])
        # logging.debug("joined file_type {}".format(file_type))

    def skip_dynamic_files(self):
        self.linker_list = {each_file for each_file in self.linker_list if not (
                re.match(global_settings.so_pattern, each_file.strip()) or re.match(global_settings.dll_pattern,
                                                                                    each_file.strip()))}
        self.cov_linker_files_set = {each_file for each_file in self.cov_linker_files_set if not (
                re.match(global_settings.so_pattern, each_file.strip()) or re.match(global_settings.dll_pattern,
                                                                                    each_file.strip()))}

    def skip_pkg_mgr(self, basefiles_dict):
        bdba_dict = {}
        pkg_dict = {}
        for basefile, paths_list in basefiles_dict.items():
            bdba_dict[basefile] = paths_list
        return pkg_dict, bdba_dict

    def set_csv_matchtpye(self):
        """
        this function reads raw_bdio.csv and sets matchtype based on hub_version
        """
        if (PKG_MGR_MODE in self.run_modes or ALL_MODE in self.run_modes):  # and
            logging.info("Attempting to use offline files for package manager at location: {}".format(
                os.path.join(self.output_dir, 'raw_bdio.csv')))
            if os.path.exists(os.path.join(self.output_dir, 'raw_bdio.csv')):
                logging.info("found package manager csv file")
                raw_bdio_df = pd.read_csv(os.path.join(self.output_dir, 'raw_bdio.csv'), encoding = util.get_encoding(os.path.join(self.output_dir, 'raw_bdio.csv')))
                self.set_matchtype_per_hub_version()
                raw_bdio_df['matchType'] = self.direct_match_evidence
                raw_bdio_df['trans-dep'] = raw_bdio_df['trans-dep'].apply(
                    lambda x: x.replace('unknown', self.transitive_match_evidence))
                raw_bdio_df.to_csv(self.csv_file_path, index=False)
            else:
                logging.error(
                    "Unable to find previously generated offline files for package manager..please make sure use_offline_files and run_modes are set correctly")

    def set_matchtype_per_hub_version(self):
        """ this function gets hub version information and sets matchtype"""
        hub_version = self.hub_api.get_hub_version()
        logging.info("BLACK DUCK VERSION IS {}".format(hub_version))
        vers_result = hub_version.split(".")
        if (int(vers_result[0]) >= 2021 and int(vers_result[1]) >= 6) or int(vers_result[0]) >= 2022:
            self.direct_match_evidence = 'DIRECT_DEPENDENCY_BINARY'
            self.transitive_match_evidence = 'TRANSITIVE_DEPENDENCY_BINARY'
        else:
            self.direct_match_evidence = 'Binary'
            self.transitive_match_evidence = 'Binary'

    async def run(self):
        run_mode_res = PKG_MGR_MODE in self.run_modes or ALL_MODE in self.run_modes
        if not self.use_offline_files:
            self.run_log_parser()

            if self.skip_dynamic:
                self.skip_dynamic_files()

            start_file_dict = datetime.now()
            self.file_dict['executable'] = self.get_files(self.executable_list)
            self.file_dict['linker'] = self.get_files(self.linker_list)
            self.file_dict['header'] = self.get_files(self.header_list)

            self.cov_file_dict['cov-executable'] = self.get_files(self.cov_executable_files_set)
            self.cov_file_dict['cov-linker'] = self.get_files(self.cov_linker_files_set)
            self.cov_file_dict['cov-header'] = self.get_files(self.cov_header_files_set)
            end_file_dict = datetime.now()
            logging.debug(
                "time taken to create dictionary from parsed and json files {}".format(end_file_dict - start_file_dict))

            logging.info("number of distinct executable files are {}".format(len(self.file_dict['executable'])))
            logging.info("number of distinct linker files are {}".format(len(self.file_dict['linker'])))
            logging.info("number of distinct header files are {}".format(len(self.file_dict['header'])))

            logging.info("coverity json - number of distinct executable files are {}".format(
                len(self.cov_file_dict['cov-executable'])))
            logging.info(
                "coverity json - number of distinct linker files are {}".format(len(self.cov_file_dict['cov-linker'])))
            logging.info(
                "coverity json - number of distinct header files are {}".format(len(self.cov_file_dict['cov-header'])))
            self.write_to_txt(self.file_dict, self.binary_files_path)
            self.unresol_set = set(
                list(self.file_dict['executable'].keys()) + list((self.file_dict['linker'].keys())) + list(
                    (self.file_dict['header'].keys())))
            logging.info("total number of unresolved files at beginning are : {}".format(len(self.unresol_set)))

            self.build_dir_dict = self.generate_build_dir_files()
            # logging.debug("number of distinct build dir files are {}".format(len(self.build_dir_dict)))

            start_resolv = datetime.now()
            self.resolved_file_dict['executable'], self.unresolved_file_dict['executable'] = self.resolve_file_paths(
                self.file_dict['executable'])
            self.resolved_file_dict['linker'], self.unresolved_file_dict['linker'] = self.resolve_file_paths(
                self.file_dict['linker'])
            self.resolved_file_dict['header'], self.unresolved_file_dict['header'] = self.resolve_file_paths(
                self.file_dict['header'])

            self.resolved_cov_file_dict['cov-executable'], self.unresolved_cov_file_dict[
                'cov-executable'] = self.resolve_file_paths(
                self.cov_file_dict['cov-executable'])
            self.resolved_cov_file_dict['cov-linker'], self.unresolved_cov_file_dict[
                'cov-linker'] = self.resolve_file_paths(
                self.cov_file_dict['cov-linker'])
            self.resolved_cov_file_dict['cov-header'], self.unresolved_cov_file_dict[
                'cov-header'] = self.resolve_file_paths(
                self.cov_file_dict['cov-header'])

            logging.debug("total resolved files: {} and total unresolved files : {} for executables".format(
                len(self.resolved_file_dict['executable']), len(self.unresolved_file_dict['executable'])))
            logging.debug("total resolved files: {} and total unresolved files : {} for linker".format(
                len(self.resolved_file_dict['linker']), len(self.unresolved_file_dict['linker'])))
            logging.debug("total resolved files: {} and total unresolved files : {} for header".format(
                len(self.resolved_file_dict['header']), len(self.unresolved_file_dict['header'])))

            logging.debug(
                "coverity json - total resolved files: {} and total unresolved files : {} for executables".format(
                    len(self.resolved_cov_file_dict['cov-executable']),
                    len(self.unresolved_cov_file_dict['cov-executable'])))
            logging.debug("coverity json - total resolved files: {} and total unresolved files : {} for linker".format(
                len(self.resolved_cov_file_dict['cov-linker']), len(self.unresolved_cov_file_dict['cov-linker'])))
            logging.debug("coverity json - total resolved files: {} and total unresolved files : {} for header".format(
                len(self.resolved_cov_file_dict['cov-header']), len(self.unresolved_cov_file_dict['cov-header'])))

            self.difference_dict = {}
            self.difference_dict['extra-exe-in-json'], self.difference_dict[
                'extra-exe-in-grep'] = self.get_dict_difference(self.resolved_cov_file_dict['cov-executable'],
                                                                self.resolved_file_dict['executable'])
            self.difference_dict['extra-linker-in-json'], self.difference_dict[
                'extra-linker-in-grep'] = self.get_dict_difference(self.resolved_cov_file_dict['cov-linker'],
                                                                   self.resolved_file_dict['linker'])
            self.difference_dict['extra-header-in-json'], self.difference_dict[
                'extra-header-in-grep'] = self.get_dict_difference(self.resolved_cov_file_dict['cov-header'],
                                                                   self.resolved_file_dict['header'])

            logging.info("total executables present in json not present in grep are : {}".format(
                len(self.difference_dict['extra-exe-in-json'])))
            logging.info("total linker present in json not present in grep are : {}".format(
                len(self.difference_dict['extra-linker-in-json'])))
            logging.info("total header present in json not present in grep are : {}".format(
                len(self.difference_dict['extra-header-in-json'])))
            logging.info("total executables present in grep not present in json are : {}".format(
                len(self.difference_dict['extra-exe-in-grep'])))
            logging.info("total linker present in grep not present in json are : {}".format(
                len(self.difference_dict['extra-linker-in-grep'])))
            logging.info("total header present in grep not present in json are : {}".format(
                len(self.difference_dict['extra-header-in-grep'])))

            self.write_to_txt(self.resolved_file_dict, self.resolved_files_path)
            self.write_to_txt(self.unresolved_file_dict, self.unresolved_files_path)
            self.write_to_txt(self.difference_dict, self.json_grep_files_list)
            self.write_to_txt(self.resolved_cov_file_dict, self.resolved_cov_files_path)
            self.write_to_txt(self.unresolved_cov_file_dict, self.unresolved_cov_files_path)

            # join here cov-json and grep
            self.join_json_grep(self.resolved_cov_file_dict['cov-linker'], 'linker')
            self.join_json_grep(self.resolved_cov_file_dict['cov-header'], 'header')
            self.join_json_grep(self.resolved_cov_file_dict['cov-executable'], 'executable')

            logging.debug("after join: total resolved files: {} and total unresolved files : {} for executables".format(
                len(self.resolved_file_dict['executable']), len(self.unresolved_file_dict['executable'])))
            logging.debug("after join: total resolved files: {} and total unresolved files : {} for linker".format(
                len(self.resolved_file_dict['linker']), len(self.unresolved_file_dict['linker'])))
            logging.debug("after join: total resolved files: {} and total unresolved files : {} for header".format(
                len(self.resolved_file_dict['header']), len(self.unresolved_file_dict['header'])))

            end_resolv = datetime.now()
            logging.debug(
                "time taken to resolve paths and join parse files with json files {}".format(end_resolv - start_resolv))

            # check hub version if online or take version input from user
        logging.debug("self.offline mode is {}".format(self.offline))
        logging.debug("self.use_offline_files is {}".format(self.use_offline_files))

        if self.offline:
            self.direct_match_evidence = 'unknown'
            self.transitive_match_evidence = 'unknown'
        else:
            self.set_matchtype_per_hub_version()

        if not self.use_offline_files:
            start_pkg = datetime.now()
            if run_mode_res:
                logging.debug("self.direct match evd is {}".format(self.direct_match_evidence))
                logging.debug("self.trans match evd is {}".format(self.transitive_match_evidence))

                self.pkg_mgr_data['linker'], self.bdba_data['linker'] = await self.check_pkg_mgr(
                    self.resolved_file_dict['linker'])
                self.pkg_mgr_data['header'], self.bdba_data['header'] = await self.check_pkg_mgr(
                    self.resolved_file_dict['header'])
            else:
                self.pkg_mgr_data['linker'], self.bdba_data['linker'] = self.skip_pkg_mgr(
                    self.resolved_file_dict['linker'])
                self.pkg_mgr_data['header'], self.bdba_data['header'] = self.skip_pkg_mgr(
                    self.resolved_file_dict['header'])
            # add pkg_mgr_data['linker'] and pkg_mgr_data['header'] to seen files
            self.seen_files_for_pkg_mgr.update(self.pkg_mgr_data['linker'])
            self.seen_files_for_pkg_mgr.update(self.pkg_mgr_data['header'])

            end_pkg = datetime.now()
            logging.info("time taken to get package manager results {}".format(end_pkg - start_pkg))

            logging.info("length of pkg_mgr_data for linker is {}".format(len(self.pkg_mgr_data['linker'])))
            logging.info("length of bdba_data for linker is {}".format(len(self.bdba_data['linker'])))
            logging.debug("bdba_data for linker is {}".format(self.bdba_data['linker']))

            logging.info("length of pkg_mgr_data for header is {}".format(len(self.pkg_mgr_data['header'])))
            logging.info("length of bdba_data for header is {}".format(len(self.bdba_data['header'])))
            logging.debug("bdba_data for header is {}".format(self.bdba_data['header']))

            if self.can_perform_ldd() and not self.skip_transitives and not self.skip_dynamic and run_mode_res:
                start_ldd = datetime.now()
                self.ldd_linker, self.bdba_data['ldd_linker'] = await self.check_ldd(self.pkg_mgr_data['linker'])
                logging.debug("ldd_linker is {}".format(self.ldd_linker))
                logging.info("length of ldd_linker is {}".format(len(self.ldd_linker)))
                logging.info("length of bdba_data for ldd_linker is {}".format(len(self.bdba_data['ldd_linker'])))
                logging.debug("bdba_data for ldd_linker is {}".format(self.bdba_data['ldd_linker']))
                end_ldd = datetime.now()
                logging.info("time taken to get ldd results {}".format(end_ldd - start_ldd))
                logging.debug("dups count for ldd is {}".format(self.dups_count))

                self.lddebug_executable, self.bdba_data['lddebug_exe'] = await self.check_ldd_deb(
                    self.resolved_file_dict['executable'])
                logging.debug("lddebug_executable is {}".format(self.lddebug_executable))
                logging.info("length of lddebug_executable is {}".format(len(self.lddebug_executable)))
                logging.info(
                    "length of bdba_data for lddebug_executable is {}".format(len(self.bdba_data['lddebug_exe'])))
                logging.debug("bdba_data for lddebug_executable is {}".format(self.bdba_data['lddebug_exe']))
                end_ldd_deb = datetime.now()
                logging.info("time taken to get ld debug results {}".format(end_ldd_deb - end_ldd))
                logging.debug("dups count for ld debug is {}".format(self.dups_count))
                logging.info("len of all files are {}".format(len(self.seen_files_for_pkg_mgr)))

            if run_mode_res:
                self.final_components_dict = await self.check_components()
                logging.debug("final_components_dict is  {}".format(self.final_components_dict))
                logging.info("length of final_components_dict is {}".format(len(self.final_components_dict)))
                self.parse_components_info()  ## csv created in offline/online mode
                logging.info("length of csv file is {}".format(len(self.csv_file_path)))
                if not self.offline:
                    self.csv_to_json()
                    logging.info("length of json file is {}".format(len(self.json_file_path)))
            if BDBA_MODE in self.run_modes or ALL_MODE in self.run_modes:
                self.zip_files()
            return "package manager run completed"
        else:  ## if use_offline_files is set to True
            if run_mode_res:
                self.set_csv_matchtpye()
                self.csv_to_json()
            return "package manager run completed"

