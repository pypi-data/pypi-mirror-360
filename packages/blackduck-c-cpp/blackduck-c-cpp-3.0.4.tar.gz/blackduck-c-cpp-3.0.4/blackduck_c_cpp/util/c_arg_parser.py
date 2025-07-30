"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import configargparse
import os
import yaml


class C_Parser:

    @staticmethod
    def required_dir_exists(path):
        # Check input does not contain spaces
        if not os.path.exists(path):
            msg = " No buildable directory found at {}".format(path)
            raise configargparse.ArgumentTypeError(msg)
        return path

    @staticmethod
    def str2bool(v):
        # convert possible options for boolean values into a bool itself.
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise configargparse.ArgumentTypeError('Boolean value expected.')

    def __init__(self):
        # from: https://realpython.com/command-line-interfaces-python-argparse/

        self.parser = configargparse.ArgParser(description='Capture all build files and send for analysis.', )

        self.parser.add_argument('-c', '--config', is_config_file=True, help='Configuration file path.')

        # Add the arguments
        self.parser.add_argument('-bc', '--build_cmd',
                                 metavar='build_cmd',
                                 dest='build_cmd',
                                 default='',
                                 type=str,
                                 help='Command used to execute the build')

        self.parser.add_argument('-d', '--build_dir',
                                 required=True,
                                 type=C_Parser.required_dir_exists,
                                 help='Directory from which to run build')

        self.parser.add_argument('-Cov', '--coverity_root',
                                 metavar='coverity_root',
                                 dest='coverity_root',
                                 default='',
                                 type=str,
                                 help="Base directory for coverity. If not specified, blackduck-c-cpp downloads latest mini coverity package from GCP for authorized Black Duck customers for Black Duck versions >= 2021.10. For downloading coverity package using GCP, you need to open connection toward *.googleapis.com:443. If you don't have coverity package and your Black Duck version is < 2021.10, please contact sales team to get latest version of coverity package.")

        self.parser.add_argument('-Cd', '--cov_output_dir',
                                 metavar='cov_output_dir',
                                 dest='cov_output_dir',
                                 default='',
                                 type=str,
                                 help='Target directory for coverity output files.If not specified, defaults to user_home/.blackduck/blackduck-c-cpp/output/project_name')

        self.parser.add_argument('-od', '--output_dir',
                                 metavar='output_dir',
                                 dest='output_dir',
                                 default='',
                                 type=str,
                                 help='Target directory for blackduck-c-cpp output files.If not specified, defaults to user_home/.blackduck/blackduck-c-cpp/output/project_name. output_dir should be outside of the build directory.')

        self.parser.add_argument('-s', '--skip_build',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skip build and use previously generated build data. Make sure that your initial coverity wrapped build uses the --emit-link-units flag')

        self.parser.add_argument('-v', '--verbose',
                                 metavar='verbose',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Verbose mode selection')

        self.parser.add_argument('-proj', '--project_name',
                                 required=True,
                                 dest='project_name',
                                 type=str,
                                 help='Black Duck project name')

        self.parser.add_argument('-vers', '--project_version',
                                 required=True,
                                 dest='project_version',
                                 type=str,
                                 help='Black Duck project version')

        self.parser.add_argument('-Cl', '--codelocation_name',
                                 dest='codelocation_name',
                                 type=str,
                                 help="This controls the Black Duck's codelocation.  The codelocation_name will overwrite any scans sent to the same codelocation_name, indicating that this is a new scan of a previous code location.  Use with care.")

        self.parser.add_argument('-bd', '--bd_url',
                                 required=True,
                                 metavar='bd_url',
                                 type=str,
                                 help='Black Duck URL')

        self.parser.add_argument('-a', '--api_token',
                                 dest='api_token',
                                 metavar='api_token',
                                 type=str,
                                 help='Black Duck API token')

        self.parser.add_argument('-as', '--additional_sig_scan_args',
                                 metavar='additional_sig_scan_args',
                                 dest='additional_sig_scan_args',
                                 type=str,
                                 default=None,
                                 help='Any additional args to pass to the signature scanner. IndividualFileMatching is by default turned on. To pass multiple params, you can pass it like additional_sig_scan_args: \'--snippet-matching --license-search\'. It accepts scan cli properties; Detect properties are not accepted here.')

        self.parser.add_argument('-i', '--insecure',
                                 dest='insecure',
                                 metavar='insecure',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Disable SSL verification so self-signed Black Duck certs will be trusted')

        self.parser.add_argument('-f', '--force',
                                 dest='force',
                                 metavar='force',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='In case of GCP failure, force use of older version of Coverity (if present)')

        self.parser.add_argument('-djs', '--disable_bdio_json_splitter',
                                 dest='disable_bdio_json_splitter',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Disable the json splitter and always upload as a single scan. For using json/bdio splitter, dryrun is needed, so please run in offline mode first.')

        self.parser.add_argument('-si', '--scan_interval',
                                 dest='scan_interval',
                                 type=int,
                                 default=60,
                                 help='Set the number of seconds to wait between scan uploads in case of multiple scans')

        self.parser.add_argument('-jsl', '--json_splitter_limit',
                                 dest='json_splitter_limit',
                                 default=4750000000,
                                 metavar='json_splitter_limit',
                                 type=int,
                                 help='Set the limit for a scan size in bytes. For using json/bdio splitter, dryrun is needed, so please run in offline mode first.')

        self.parser.add_argument('-bsfl', '--bdio_split_max_file_entries',
                                 dest='bdio_split_max_file_entries',
                                 default=100000,
                                 metavar='bdio_split_max_file_entries',
                                 type=int,
                                 help='Set the limit for maximum scan node entries per generated BDIO file')

        self.parser.add_argument('-bscn', '--bdio_split_max_chunk_nodes',
                                 dest='bdio_split_max_chunk_nodes',
                                 default=3000,
                                 metavar='bdio_split_max_chunk_nodes',
                                 type=int,
                                 help='Set the limit for maximum scan node entries per single bdio-entry file')

        self.parser.add_argument('-dg', '--debug',
                                 metavar='debug',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Debug mode selection. Setting debug: True sends all the files we found to all matching types. By default, it will only send files not detected by package manager to BDBA and Signature matching.')

        self.parser.add_argument('-st', '--skip_transitives',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skipping all transitive dependencies')

        self.parser.add_argument('-sh', '--skip_includes',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skipping all .h & .hpp files from all types of scan')

        self.parser.add_argument('-sd', '--skip_dynamic',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Skipping all dynamic (.so/.dll) files from all types of scan')

        self.parser.add_argument('-off', '--offline',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Store bdba and sig zip files, sig scan json, and raw_bdio.csv to disk if offline mode is true. For scans over 5GB to use bdio/json splitter, please run in offline mode first. scan_cli_dir should be specified when run in offline mode to generate dryrun files.  Once the dryrun files are generated, use_offline_files: True can be set to upload those to hub.')

        self.parser.add_argument('-md', '--modes',
                                 metavar='modes',
                                 dest='modes',
                                 type=str,
                                 default="ALL",
                                 help="Comma separated list of modes to run - 'all'(default),'bdba','sig','pkg_mgr'")

        self.parser.add_argument('-uo', '--use_offline_files',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Use offline generated files for upload in online mode')

        self.parser.add_argument('-sc', '--scan_cli_dir',
                                 metavar='scan_cli_dir',
                                 dest='scan_cli_dir',
                                 default=None,
                                 type=str,
                                 help='Scan cli directory. Ex: Providing scan_cli_dir as /home/../../Black_Duck_Scan_Installation/ instead of /home/../../Black_Duck_Scan_Installation/scan.cli-2022.4.0/ works.')

        self.parser.add_argument('-Cc', '--cov_configure_args',
                                 metavar='cov_configure_args',
                                 dest='cov_configure_args',
                                 default={},
                                 type=yaml.safe_load,
                                 required=False,
                                 help='Additional configuration commands to cov-configure for different compilers. Inputs taken are of format {"compiler":"compiler-type"}. There is a way to use coverity template configuration to reduce number of template compiler configurations with wildcards: example: "--compiler *g++ --comptype gcc" for adding x86_64-pc-linux-gnu-g++ can be passed as cov_configure_args: {"*g++":"gcc"}')

        self.parser.add_argument('-ac', '--additional_coverity_params',
                                 metavar='additional_coverity_params',
                                 dest='additional_coverity_params',
                                 type=str,
                                 default=None,
                                 help='Any additional args to pass to coverity build command. example: "--record-with-source"')

        self.parser.add_argument('-es', '--expand_sig_files',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help='Use expand_sig_files for creating exploded directory instead of zip in sig scanner mode')

        self.parser.add_argument('-po', '--port',
                                 type=int,
                                 default=443,
                                 help='Set a custom Black Duck port')

        self.parser.add_argument('-ba', '--bazel',
                                 type=C_Parser.str2bool,
                                 nargs='?',
                                 const=True,
                                 default=False,
                                 help="Use if this is a bazel build - make sure you have followed the setup instructions for Coverity")

        self.parser.add_argument('-pgn', '--project_group_name',
                                 dest='project_group_name',
                                 type=str,
                                 help="This is same as --detect.project.group.name in detect. Sets the 'Project Group' to assign the project to. Must match exactly to an existing project group on Black Duck.")

        self.parser.add_argument('-pgd', '--project_description',
                                 dest='project_description',
                                 type=str,
                                 default=None,
                                 help="This is same as --detect.project.description in detect. If project description is specified, your project will be created with this description.")

        self.parser.add_argument('-scv', '--set_coverity_mode',
                                 metavar='set_coverity_mode',
                                 dest='set_coverity_mode',
                                 type=str,
                                 default=None,
                                 help="specify coverity mode to 'cov-build' to force run with cov-build. cov-cli runs by default for coverity versions >= 2023.9 and cov-build for < 2023.9")

        self.parser.add_argument('-fpc', '--force_pull_coverity_vers',
                                 metavar='force_pull_coverity_vers',
                                 dest='force_pull_coverity_vers',
                                 type=str,
                                 default=None,
                                 help="For linux platforms, force pull 2022.9 or latest version of coverity if not auto downloaded by blackduck-c-cpp correctly by specifying -'old' or 'latest' respectively")

        self.args = self.parser.parse_args()
