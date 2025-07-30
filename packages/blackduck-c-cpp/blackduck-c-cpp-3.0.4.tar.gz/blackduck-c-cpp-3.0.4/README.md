# blackduck-c-cpp

This code is responsible for running a c/cpp build wrapped by Coverity - capturing the source and binary files involved
and then using the available tools to deliver BDIO and signatures to Black Duck using a variety of tools and
methodologies.

## Overview

C and CPP projects don't have a standard package manager or method for managing dependencies. It is therefore more
difficult to create an accurate BOM for these projects. This leaves Software Composition Analysis tools fewer options
than with other languages. The primary options which are available in this context are: file system signatures. Black
Duck has a variety of old and new signatures which can be used to build a BOM. In order to effectively use signatures,
the tool first needs to know which files to take signatures from. In the past SCA tools have pointed a scanner at a
build directory, getting signatures from a subset of files within the directory sub-tree. The problem with this approach
is that there are many environmental variables, parameters and switches provided to the build tools, which make
reference to files outside of the build directory to include as part of the build. Further, there are, commonly, files
within the build directory, which are not part of the build and can lead to false positives within the BOM.

The new Black Duck C/CPP tool avoids the pitfalls described above by using a feature of Coverity called Build Capture.
Coverity Build Capture, wraps your build, observing all invocations of compilers and linkers and storing the paths of
all compiled source code, included header files and linked object files. These files are then matched using a variety of
methods described in the section of this document called "The BOM".

## Supported Platforms

Debian, Redhat, Ubuntu, openSUSE, Fedora, CentOS, macOS, and Windows are supported.

The signature scan and binary scan will be completed on all supported platforms as permitted by your Black Duck license.
Any scan cli parameters can be used and passed to blackduck-c-cpp tool through the additional_sig_scan_args parameter.

On Unix-like operating systems, a package manager scan will also be run. Since Windows doesn't have a supported package
manager, blackduck-c-cpp scans run on Windows won't include the package manager scan and won't produce a BDIO file.
Here, package manager scan refers to usage of O/S package managers such as yum, apt etc.

## Supported Compilers and Linkers

Run ./cov-configure --list-compiler-types to get complete set of supported compilers

Linkers supported: gcc, msvc.

## Installation

Blackduck-c-cpp can be used with all currently supported versions of Black Duck: https://documentation.blackduck.com/bundle/blackduck-compatibility/page/topics/Support-and-Service-Schedule.html

To install from pypi:

```
pip install blackduck-c-cpp
```

To install a specific version:

```
pip install blackduck-c-cpp==3.0.4
```

## Configuration

Prior to running your build, run any build specific configuration needed. Then the blackduck-c-cpp tool can either be
configured using a .yaml file or with command line arguments.

Here is a sample fully functional .yaml configuration: ardour-config.yaml

```
build_cmd: ../waf build
build_dir: /Users/theUser/myProject/ardour/build/
skip_build: False
verbose: True
project_name: ardour_mac
project_version: may-4-2021
bd_url: https://...
api_token: <token>
insecure: False
```

### API Token

Black Duck API tokens are generated on a per-user basis. To scan to a new project and view the results, the user who
generates the API token for blackduck-c-cpp must at minimum have the **Global Code Scanner** and **Global Project 
Administrator** roles assigned. To scan to an existing project and view the results, the user must at
minimum have the project assigned to their user, and have the **Project Code Scanner** role assigned. See 
Administration > Managing Black Duck user accounts > Understanding roles in the Black Duck Help documentation for more 
details on user roles. The Black Duck Help documentation is accessible through the Black Duck UI.

To generate an API token:

1. Go to the Black Duck UI and log in.
2. From the user menu located on the top navigation bar, select My Access Tokens.
3. Click Create New Token. The Create New Token dialog box appears.
4. Enter a name, description (optional), and select the scope for this token (to use with blackduck-c-cpp, must be **
   read and write access**).
5. Click Create. The Access Token Name dialog box appears with the access token.
6. Copy the access token shown in the dialog box. This token can only be viewed here at this time. Once you close the
   dialog box, you cannot view the value of this token.

### Bazel

Bazel is supported in Coverity starting in versions 2022.3.0+ and blackduck-c-cpp in versions 1.0.13+.

To enable, use the `--bazel` switch (or set `bazel: True` in your yaml configuration file), but additional Coverity
setup is required as described below.

Bazel builds can be captured on the x86_64 versions of Windows, Linux, and macOS that are supported by Coverity
Analysis.

Compilers for Coverity analysis are supported, but all compilers must be accessible and runnable on the host system:
Remote cross-platform builds are not supported.

#### Bazel Setup

##### Bazel coverity 2024.6 documentation: 
https://documentation.blackduck.com/bundle/coverity-docs/page/coverity-analysis/topics/building_with_bazel.html

##### Modify project files

###### Workspace file

Like other Bazel integrations, the Coverity integration has an archive of rules to be used by the build.

blackduck-c-cpp will attempt to automatically update this file as required if it hasn't already been modified by the
user. If the automatic update fails, the failure will be logged and the user will need to complete the following steps
manually.

The WORKSPACE (or WORKSPACE.bazel) file defines the root of the Bazel project, and it needs to be modified to reference
the Coverity integration. If you are supplying your own Coverity installation, the Coverity integration can be found in
the Coverity Analysis installation at

```
<Coverity Analysis installation path>/bazel/rules_coverity.tar.gz
```

If you are using the mini package provided by blackduck-c-cpp, then by default the Coverity integration can be found in
the Coverity Analysis installation at

```
`<User home>/.blackduck/blackduck-c-cpp/cov-build-capture/bazel/rules_coverity.tar.gz`
```

You can remove it from the installation and host it anywhere convenient.

Assuming the integration archive is available on a network share at `/mnt/network-share/rules_coverity.tar.gz,` append
the following snippet onto your WORKSPACE file:

```
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
http_archive(
    name="rules_coverity",
    urls=["file:///mnt/network-share/rules_coverity.tar.gz"],
)
  
  
load("@rules_coverity//coverity:repositories.bzl", "rules_coverity_toolchains")
rules_coverity_toolchains()
```

You can use different URLs, depending on whether the integration archive is available locally, on a file share, or
through HTTP. The only part of the kit that is necessary for this is the integration archive, so it can be placed
wherever needed, independently of the rest of the kit. Bazel can fetch from "file://", "http://" and "https://" URLs.
The "urls" field is a list - multiple URLs can be specified, and fetching the integration from them will be attempted in
order.

Attention: If you:

- are using Bazel 7 or a newer version, and

- are adding Coverity to your Bazel integration in the WORKSPACE file, and

- have Bazel modules enabled for other purposes,
then probably you need to explicitly add dependencies to your MODULE.bazel file for use by the Coverity rules_cc and platforms fields. The versions that have been tested with Coverity are 0.0.9 for rules_cc and 0.0.5 for platforms; specifying newer or older versions might also work. The lines to add to MODULE.bazel are as follows:

```
bazel_dep(name="rules_cc", version="0.0.9")
bazel_dep(name="platforms", version="0.0.5")
```

###### Module file
If you’re using Bazel 7 or a newer version, Coverity can be integrated using the MODULE.bazel file instead of the WORKSPACE file. The module file defines Bazel modules that should be used by your build. To do this, you must first either include the rules_coverity module in a registry you control, or use the cov-setup-bazel-registry tool to set up a local registry that contains that module; instructions on how to do this can be found in Bazel registry setup.

To integrate Coverity into the MODULE.bazel file, just add the following line:

bazel_dep(name="rules_coverity", version="2024.6.0")

###### Performing the build
Once you have set up the WORKSPACE or MODULE.bazel files, you can run blackduck-c-cpp command with build command as bazel build //my-bazel-target.

Example blackduck-c-cpp config file for bazel to build Google's open source abseil-cpp library (https://github.com/abseil/abseil-cpp) 
```
build_cmd: bazel build //absl/strings:strings
build_dir: /apps/abseil/abseil-cpp/
skip_build: False
verbose: True
project_name: abseil
project_version: 1.0v
bd_url: <bd_url>
api_token: <api_token>
set_coverity_mode: cov-build
bazel: True
```

#####  When using older versions of coverity like 2023.9, please follow below steps:

##### Modify project files

###### Workspace file

Like other Bazel integrations, the Coverity integration has an archive of rules to be used by the build.

blackduck-c-cpp will attempt to automatically update this file as required if it hasn't already been modified by the
user. If the automatic update fails, the failure will be logged and the user will need to complete the following steps
manually.

The WORKSPACE (or WORKSPACE.bazel) file defines the root of the Bazel project, and it needs to be modified to reference
the Coverity integration. If you are supplying your own Coverity installation, the Coverity integration can be found in
the Coverity Analysis installation at

```
<Coverity Analysis installation path>/bazel/rules_coverity.tar.gz
```

If you are using the mini package provided by blackduck-c-cpp, then by default the Coverity integration can be found in
the Coverity Analysis installation at

```
`<User home>/.blackduck/blackduck-c-cpp/cov-build-capture/bazel/rules_coverity.tar.gz`
```

You can remove it from the installation and host it anywhere convenient.

Assuming the integration archive is available on a network share at `/mnt/network-share/rules_coverity.tar.gz,` append
the following snippet onto your WORKSPACE file:

```
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
http_archive(
    name="rules_coverity",
    urls=["file:///mnt/network-share/rules_coverity.tar.gz"],
)
  
  
load("@rules_coverity//coverity:repositories.bzl", "rules_coverity_toolchains")
rules_coverity_toolchains()
```

You can use different URLs, depending on whether the integration archive is available locally, on a file share, or
through HTTP. The only part of the kit that is necessary for this is the integration archive, so it can be placed
wherever needed, independently of the rest of the kit. Bazel can fetch from "file://", "http://" and "https://" URLs.
The "urls" field is a list - multiple URLs can be specified, and fetching the integration from them will be attempted in
order.

###### Build file

Unlike the WORKSPACE file, blackduck-c-cpp can't update the BUILD file automatically. This must be completed by the
user.

Bazel uses the BUILD (or BUILD.bazel) file to do the following:

- Mark a package boundary
- Declare what targets can be built in that package
- Specify how to build those targets

The Coverity-Bazel integration needs a new target added that depends on existing targets to generate a "build
description" of all the build commands that would have been executed in the building of those targets. If you had,
for example, a build with two separate targets that you wanted to capture, the BUILD file would start out looking
something like this:

```
load("@rules_cc//cc:defs.bzl", "cc_binary")​
cc_binary(name="foo", srcs=["foo.cc"])
cc_binary(name="bar", srcs=["bar.cc"])
```

To capture the files (including link files) used in the building of the targets :foo and :bar (foo.cc and bar.cc,
respectively), you would
modify the BUILD file to be something like this:

```
load("@rules_cc//cc:defs.bzl", "cc_binary")
cc_binary(name="foo", srcs=["foo.cc"])
cc_binary(name="bar", srcs=["bar.cc"])
 
load("@rules_coverity//coverity:defs.bzl", "cov_enable_link", "cov_gen_script")
cov_enable_link(
    name = "enable_link",
    build_setting_default = True,
)
cov_gen_script(name="coverity-target", deps=[":foo", ":bar"], enable_link = ":enable_link",)
```

Here is an example using Google's open source abseil-cpp library (https://github.com/abseil/abseil-cpp):

Before:

```
package(default_visibility = ["//visibility:public"])

licenses(["notice"])  # Apache 2.0

# Expose license for external usage through bazel.
exports_files([
    "AUTHORS",
    "LICENSE",
])
```

After:

```
package(default_visibility = ["//visibility:public"])

licenses(["notice"])  # Apache 2.0

# Expose license for external usage through bazel.
exports_files([
    "AUTHORS",
    "LICENSE",
])

load("@rules_coverity//coverity:defs.bzl", "cov_enable_link", "cov_gen_script")
cov_enable_link(
    name = "enable_link",
    build_setting_default = True,
)
cov_gen_script(
    name="cov",
    deps = [
        "//absl/status:statusor",
        "//absl/status:status",
        "//absl/random:bit_gen_ref",
        "//absl/functional:bind_front",
        "//absl/flags:parse",
        "//absl/flags:usage",
        "//absl/flags:flag",
        "//absl/debugging:leak_check",
        "//absl/debugging:failure_signal_handler",
        "//absl/debugging:leak_check_disable",
        "//absl/container:node_hash_set",
        "//absl/container:hashtable_debug",
        "//absl/random:random",
        "//absl/random:seed_sequences",
        "//absl/random:seed_gen_exception",
        "//absl/random:distributions",
        "//absl/container:flat_hash_set",
        "//absl/types:any",
        "//absl/types:bad_any_cast",
        "//absl/container:btree",
        "//absl/types:compare",
        "//absl/cleanup:cleanup",
        "//absl/container:node_hash_map",
        "//absl/container:node_hash_policy",
        "//absl/flags:reflection",
        "//absl/container:flat_hash_map",
        "//absl/container:raw_hash_map",
        "//absl/container:raw_hash_set",
        "//absl/container:hashtablez_sampler",
        "//absl/container:hashtable_debug_hooks",
        "//absl/container:hash_policy_traits",
        "//absl/container:common",
        "//absl/container:hash_function_defaults",
        "//absl/strings:cord",
        "//absl/container:layout",
        "//absl/container:inlined_vector",
        "//absl/hash:hash",
        "//absl/types:variant",
        "//absl/types:bad_variant_access",
        "//absl/hash:city",
        "//absl/container:fixed_array",
        "//absl/container:compressed_tuple",
        "//absl/container:container_memory",
        "//absl/flags:marshalling",
        "//absl/strings:str_format",
        "//absl/numeric:representation",
        "//absl/functional:function_ref",
        "//absl/flags:config",
        "//absl/flags:commandlineflag",
        "//absl/types:optional",
        "//absl/types:bad_optional_access",
        "//absl/utility:utility",
        "//absl/synchronization:synchronization",
        "//absl/time:time",
        "//absl/debugging:symbolize",
        "//absl/strings:strings",
        "//absl/numeric:int128",
        "//absl/numeric:bits",
        "//absl/debugging:stacktrace",
        "//absl/types:span",
        "//absl/memory:memory",
        "//absl/algorithm:container",
        "//absl/meta:type_traits",
        "//absl/algorithm:algorithm",
    ],
    enable_link = ":enable_link",
)
```

###### Customization: compilation mnemonics

Which Bazel actions are treated as build commands is determined by the mnemonic of the action. For now, the only
mnemonics that are treated as a build commands by default are CppCompile, Javac and Compile. These are the mnemonics
that the builtin cc_binary/cc_library rules, the builtin java_binary/java_library rules and the standard
csharp_binary/csharp_library rules use for their compilation actions, respectively. If you have custom rules that
generate actions that should be treated as build commands, modify the BUILD file again, extending from this:

```
load("@rules_cc//cc:defs.bzl", "cc_binary")
cc_binary(name="foo", srcs=["foo.cc"])
cc_binary(name="bar", srcs=["bar.cc"])
 
load("@rules_coverity//coverity:defs.bzl", "cov_gen_script")
cov_gen_script(name="coverity-target", deps=[":foo", ":bar"])
```

to something like the following:

```
load("@rules_cc//cc:defs.bzl", "cc_binary")
cc_binary(name="foo", srcs=["foo.cc"])
cc_binary(name="bar", srcs=["bar.cc"])
 
load(
    "@rules_coverity//coverity:defs.bzl", 
    "cov_gen_script", 
    "cov_compile_mnemonics"
    )
cov_compile_mnemonics(
    name="extra_mnemonics", 
    build_setting_default=["FirstMnemonic", "SecondMnemonic"]
    )
cov_gen_script(
    name="coverity-target", 
    deps=[":foo", ":bar"], 
    extra_compile_mnemonics=":extra_mnemonics"
    )
```

### Details

usage: blackduck-c-cpp [-h] [-c CONFIG] [-bc build_cmd] -d
BUILD_DIR [-Cov coverity_root] [-Cd cov_output_dir] [-od output_dir] [-s [SKIP_BUILD]] [-v [verbose]] -proj PROJECT_NAME
-vers PROJECT_VERSION [-Cl CODELOCATION_NAME] -bd bd_url [-a api_token] [-as additional_sig_scan_args] [-i [insecure]] [
-f [force]] [-djs [DISABLE_BDIO_JSON_SPLITTER]] [-si SCAN_INTERVAL] [-jsl json_splitter_limit] [-bsfl bdio_split_max_file_entries] [-bscn bdio_split_max_chunk_nodes] [
-dg [debug]] [-st [SKIP_TRANSITIVES]] [-sh [SKIP_INCLUDES]] [
-sd [SKIP_DYNAMIC]] [-off [OFFLINE]] [-md modes] [-uo [USE_OFFLINE_FILES]] [-sc scan_cli_dir] [-Cc cov_configure_args] [-ac additional_coverity_params] [-es [EXPAND_SIG_FILES]] [-po PORT] [-ba [BAZEL]] [-pgn PROJECT_GROUP_NAME] [-pgd PROJECT_DESCRIPTION] [-scv set_coverity_mode] [-fpc force_pull_coverity_vers]

```
options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file path.
  -bc build_cmd, --build_cmd build_cmd
                        Command used to execute the build
  -d BUILD_DIR, --build_dir BUILD_DIR
                        Directory from which to run build
  -Cov coverity_root, --coverity_root coverity_root
                        Base directory for coverity. If not specified, blackduck-c-cpp downloads latest mini coverity package from GCP for authorized Black Duck customers
                        for Black Duck versions >= 2021.10. For downloading coverity package using GCP, you need to open connection toward *.googleapis.com:443. If you
                        don't have coverity package and your Black Duck version is < 2021.10, please contact sales team to get latest version of coverity package.
  -Cd cov_output_dir, --cov_output_dir cov_output_dir
                        Target directory for coverity output files.If not specified, defaults to user_home/.blackduck/blackduck-c-cpp/output/project_name
  -od output_dir, --output_dir output_dir
                        Target directory for blackduck-c-cpp output files.If not specified, defaults to user_home/.blackduck/blackduck-c-cpp/output/project_name. 
                        output_dir should be outside of the build directory.
  -s [SKIP_BUILD], --skip_build [SKIP_BUILD]
                        Skip build and use previously generated build data. Make sure that your initial coverity wrapped build uses the --emit-link-units flag
  -v [verbose], --verbose [verbose]
                        Verbose mode selection
  -proj PROJECT_NAME, --project_name PROJECT_NAME
                        Black Duck project name
  -vers PROJECT_VERSION, --project_version PROJECT_VERSION
                        Black Duck project version
  -Cl CODELOCATION_NAME, --codelocation_name CODELOCATION_NAME
                        This controls the Black Duck's codelocation. The codelocation_name will overwrite any scans sent to the same codelocation_name, indicating that
                        this is a new scan of a previous code location. Use with care.
  -bd bd_url, --bd_url bd_url
                        Black Duck URL
  -a api_token, --api_token api_token
                        Black Duck API token.  Instead of specifying api_token value in command line or yaml file, use the BD_HUB_TOKEN environment variable to specify a Black Duck API token.
  -as additional_sig_scan_args, --additional_sig_scan_args additional_sig_scan_args
                        Any additional args to pass to the signature scanner. IndividualFileMatching is by default turned on. To pass multiple params, you can pass it like additional_sig_scan_args: '--snippet-matching --license-search'.
                        It accepts scan cli properties; Detect properties are not accepted here.
  -i [insecure], --insecure [insecure]
                        Disable SSL verification so self-signed Black Duck certs will be trusted
  -f [force], --force [force]
                        In case of GCP failure, force use of older version of Coverity (if present)
  -djs [DISABLE_BDIO_JSON_SPLITTER], --disable_bdio_json_splitter [DISABLE_BDIO_JSON_SPLITTER]
                        Disable the json splitter and always upload as a single scan. For using json/bdio splitter, dryrun is needed, so please run in offline mode first.
  -si SCAN_INTERVAL, --scan_interval SCAN_INTERVAL
                        Set the number of seconds to wait between scan uploads in case of multiple scans
  -jsl json_splitter_limit, --json_splitter_limit json_splitter_limit
                        Set the limit for a scan size in bytes. For using json/bdio splitter, dryrun is needed, so please run in offline mode first.
  -bsfl bdio_split_max_file_entries, --bdio_split_max_file_entries bdio_split_max_file_entries
                        Set the limit for maximum scan node entries per generated BDIO file
  -bscn bdio_split_max_chunk_nodes, --bdio_split_max_chunk_nodes bdio_split_max_chunk_nodes
                        Set the limit for maximum scan node entries per single bdio-entry file
  -dg [debug], --debug [debug]
                        Debug mode selection. Setting debug: True sends all the files we found to all matching types. By default, it will only send files not detected by
                        package manager to BDBA and Signature matching.
  -st [SKIP_TRANSITIVES], --skip_transitives [SKIP_TRANSITIVES]
                        Skipping all transitive dependencies
  -sh [SKIP_INCLUDES], --skip_includes [SKIP_INCLUDES]
                        Skipping all .h & .hpp files from all types of scan
  -sd [SKIP_DYNAMIC], --skip_dynamic [SKIP_DYNAMIC]
                        Skipping all dynamic (.so/.dll) files from all types of scan
  -off [OFFLINE], --offline [OFFLINE]
                        Store bdba and sig zip files, sig scan json, and raw_bdio.csv to disk if offline mode is true.
                        For scans over 5GB to use bdio/json splitter, please run in offline mode first. 
                        scan_cli_dir should be specified when run in offline mode to generate dryrun files. 
                        Once the dryrun files are generated, use_offline_files: True can be set to upload those to hub.
  -md modes, --modes modes
                        Comma separated list of modes to run - 'all'(default),'bdba','sig','pkg_mgr'
  -uo [USE_OFFLINE_FILES], --use_offline_files [USE_OFFLINE_FILES]
                        Use offline generated files for upload in online mode
  -sc scan_cli_dir, --scan_cli_dir scan_cli_dir
                        Scan cli directory. Ex: Providing scan_cli_dir as /home/../../Black_Duck_Scan_Installation/ instead of
                        /home/../../Black_Duck_Scan_Installation/scan.cli-2022.4.0/ works.
  -Cc cov_configure_args, --cov_configure_args cov_configure_args
                        Additional configuration commands to cov-configure for different compilers. 
                        Inputs taken are of format {"compiler":"compiler-type"}. 
                        There is a way to use coverity template configuration to reduce number of template compiler configurations with wildcards: 
                        example: "--compiler *g++ --comptype gcc" for adding x86_64-pc-linux-gnu-g++ can be passed as cov_configure_args: {"*g++":"gcc"} in yaml file. 
                        In command line, it should be passed in as: -Cc '{"compiler-1":"compiler-type-1","compiler-2":"compiler-type-2"}'. Example: -Cc '{"*g++":"gcc"}'
  -ac additional_coverity_params, --additional_coverity_params additional_coverity_params
                        Any additional args to pass to coverity build command. example: "--record-with-source"
  -es [EXPAND_SIG_FILES], --expand_sig_files [EXPAND_SIG_FILES]
                        Use expand_sig_files for creating exploded directory instead of zip in sig scanner mode
  -po PORT, --port PORT
                        Set a custom Black Duck port
  -ba [BAZEL], --bazel [BAZEL]
                        Use if this is a bazel build - make sure you have followed the setup instructions for Coverity
  -pgn PROJECT_GROUP_NAME, --project_group_name PROJECT_GROUP_NAME
                        This is same as --detect.project.group.name in detect. Sets the 'Project Group' to assign the project to. Must match exactly to an existing project
                        group on Black Duck.
  -pgd PROJECT_DESCRIPTION, --project_description PROJECT_DESCRIPTION
                        This is same as --detect.project.description in detect. If project description is specified, your project will be created with this description.
  -scv set_coverity_mode, --set_coverity_mode set_coverity_mode
                        specify coverity mode to 'cov-build' to force run with cov-build. cov-cli runs by default for coverity versions >= 2023.9 and cov-build for <
                        2023.9
  -fpc force_pull_coverity_vers, --force_pull_coverity_vers force_pull_coverity_vers
                        For linux platforms, force pull 2022.9 or latest version of coverity if not auto downloaded by blackduck-c-cpp correctly by specifying -'old' or
                        'latest' respectively                        
```

#### blackduck-c-cpp 2.0.0

Here's what changed:

2.0.0 version uses cov-cli instead of cov-build by default. Coverity cli uses cov-build under the hood.
It is a layer of automation on top of cov-build and other tools.
Instead of the user having to figure out the correct cov-configure options,
Coverity CLI guesses at the right options and runs the tools automatically.  
It doesn't always work correctly, so there are options to fix things where needed.
You can also choose to run cov-build by setting following option in yaml file:
set_coverity_mode: 'cov-build'

In CentOS7, the latest version of glibc supported is 2.17. Starting with coverity build capture 2022.12.0, glibc_2.18 is
a requirement.
So, we try to auto-download an older version of Coverity, 2022.9, on linux platforms with glibc 2.17 or older.
If blackduck-c-cpp doesn't auto-download Coverity, you can forcefully download an older version by specifying following
parameter in yaml
file:
force_pull_coverity_vers: 'old'

#### Running

Once your blackduck-c-cpp tool is installed and configured as explained above, simply run the command:

blackduck-c-cpp --config /Users/theUser/myProject/ardour-config.yaml

To use snippet scanning, pass the snippet scanning parameters to the signature scanner using
--additional_sig_scan_args <snippet scanning parameter(s)>. Black Duck recommends using --snippet-matching. See Scanning
Components > Using the Signature Scanner > Running a component scan using the Signature Scanner command line in the
Black Duck Help Guide for more details.

To access the Black Duck server via a proxy, you must set a SCAN_CLI_OPTS environment variable prior to running the
scan. See Scanning Components > Using the Signature Scanner > Accessing the Black Duck server via a proxy in the Black
Duck Help Guide for details.

#### The Bom

Direct Dependencies - These are files which are being linked in to the built executable directly or header files
included by source code as identified by Coverity Build Capture.  
Package Manager - The Package Manager of the Linux system is queried about the source of the files - if recognized,
these are added to the BOM as "Direct Dependencies". Transitive Dependencies - These are files which are needed by the
Direct Dependencies. LDD - LDD is used to List the files (Dynamic Dependencies) of the Direct Dependencies. These files
are then used to query the package manager and results are added to the BOM as "Transitive Dependencies". Binary Matches
BDBA - Any linked object files not identified by the package manager are sent to BDBA (Binary) for matching. Signature
Matches - Any linked object and header files not identified by the package manager as well as all source code identified
by Coverity Build Capture are then sent to the Knowledge Base for signature matching.

## CI Builds

This projects CI build is run through GitLab-CI Pipelines, within this repository. When changes are made on
the `master` (default) branch, the version will be appended with `b` and the pipeline number as metadata. For `release/`
branches, `-rc` will be appended to the version with the pipeline number as metadata, and this will be published to
Artifactory. When changes are made to another branch (`dev/` or `bugfix/` for example), `dev` will be appended to the
version with the pipeline number, and the commit hash will be appended as metadata.

For example:

* default branch: 1.0.0b3821+abcd1234
* release branch: 1.0.0rc4820+abcd1234
* dev branch: 1.0.0dev5293+abcd1234
* release: 1.0.0

Release jobs are also run through GitLab-CI Pipelines, when tagged as per below. The version will be uploaded to
Artifactory at the end of the pipeline.

# Releasing

To release this library, simply tag this repo with a tag of the format: `vMM.mm.ff` like `v1.0.1`. This version should
match the version (minus the `v` in `setup.py`)

Be sure to increment the version in `setup.py` to the next fix version, or minor/major version as necessary. Do not add
any metadata or additional version information to the version, here.

The specific set of steps is:

- Ensure a full `python setup install` completes
- Commit changes
- Tag with `v##.##.##`, matching the version number in `setup.py`
- Push the change log changes, and tag, to GitLab
- Update the version number in `setup.py`
- Commit version change and push to GitLab

## FAQ's

1. If BOM isn't capturing all expected components, what to do?

Make sure you did a clean build. Run all clean commands and configure commands before running the blackduck-c-cpp tool
with build command.
Also, if you are using custom compilers, you have to configure it as follows:
--cov_configure_args: {"gcc.cx.a.b-ac.mips64-linux":"gcc"} where "gcc.cx.a.b-ac.mips64-linux" is compiler and "gcc" is
compiler type in yaml file.
In command line, It can be set as -Cc '{"gcc.cx.a.b-ac.mips64-linux":"gcc"}'
you can also set matchConfidenceThreshold to 0 in additional_sig_scan_args.

2. How to run snippet scanning?

Pass below command in your yaml file
`additional_sig_scan_args: '--snippet-matching' `
To run it from command line, example:
`blackduck-c-cpp -bc "make" -d "/apps/cpuminer-2.5.1/" -s False -v True -proj "cpuminer-cmd" -vers 1.0 -bd "https:<bd_url>" -a "<api_token" -as ="--snippet-matching --copyright-search" -i False`

3. Where can blackduck-c-cpp.log be found on the system?

All output files will be in
`user_home/.blackduck/blackduck-c-cpp/output/project_name`
by default if --output_dir is not given. Else, All output files will be in output_dir.

4. How to run blackduck-c-cpp?

Run with config file where are arugments are set or through command line.
Example:
`blackduck-c-cpp -c /apps/../../cpuminer-config.yaml`
or
To run it from command line,:
`blackduck-c-cpp -bc "make" -d "/apps/cpuminer-2.5.1/" -s False -proj "cpuminer-cmd" -vers 1.0 -bd "https:<bd_url>" -a "<api_token" -i False`

5. blackduck-c-cpp invokes BDBA. Do we need to be licensed for it? What happens if I don't have BDBA?

It throws `BDBA is not licensed for use with the current Black Duck instance -- will not be used` and goes to next
matching type

6. Running blackduck-c-cpp throwing import errors

Check if you installed blackduck-c-cpp from testpypi. If so, please uninstall and install from pypi for dependencies to
be automatically installed.
If you still see import errors, There may be some issues with multiple installations.
Try to create a virtual environment with python >= 3.7 version. Uninstall blackduck-c-cpp outside virtual environment
and install blackduck-c-cpp inside virtual env. Otherwise, it may be looking at wrong installation path (Can be seen in
stacktrace)
In linux environment:

```
python3 -m venv venv
source venv/bin/activate
pip3 install blackduck-c-cpp
```

7. Where to download coverity mini package?

If coverity_root is not specified, blackduck-c-cpp automatically downloads latest mini coverity package from GCP for
authorized Black Duck users for Black Duck versions >= 2021.10.
For downloading coverity package using GCP, you need to open connection toward *.googleapis.com:443.
If you don't have coverity package and your Black Duck version is < 2021.10, please contact sales team to get latest
version of coverity package.

8. BDBA upload throws an error as follows:

```
    raise RemoteDisconnected("Remote end closed connection without"
http.client.RemoteDisconnected: Remote end closed connection without response
.......
requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
```

Check your requests-toolbelt library version - `pip show requests-toolbelt`. If you have older version than 0.9.1,
install 0.9.1 version and try again.

9. Windows build - The blackduck-c-cpp process is stuck during a phase

Try giving a keyboard input by pressing enter/any other key if you still have the command prompt open where stuck. We
noticed in Windows that programs sometimes get stuck when we click into the console and enter the "selection" mode to
highlight/copy text from it.

10. Error:

```
headers.pop('Accept')
KeyError: 'Accept'
```

Do `pip show blackduck`. If you have version < 1.0.4, install 1.0.4 version and try again.

11. Windows error - `MemoryError`

Make sure you have the correct installation of python (64bit vs 32 bit) for your operating system.

12. Spaces in the paths to Coverity analysis

` /apps/.../cov\ 2021\ <vers>/bin/cov-build`
Coverity needs to be located in a directory that doesn't have a space in it.

13. Signature scan is performed on zip. Adding other sig scan arguments are not working. What to do?

Set `expand_sig_files: True`

14. How to uninstall blackduck-c-cpp?

pip uninstall blackduck-c-cpp

15. I already have a coverity build for my project. Can I use the tool?

Yes, you can set --cov_output_dir to the path where your coverity output files reside. (build-log.txt and emit
directory), then set `skip_build: True`.

16. How to see more logging information for troubleshooting?

You can see the blackduck-c-cpp.log file in output_dir  (OR) set verbose: True to see if it reveals any issues in
stdout.

17. I have custom compilers. What to do?

If you are using custom compilers, you have to configure it as follows:
cov_configure_args: {"gcc.cx.a.b-ac.mips64-linux":"gcc"} where "gcc.cx.a.b-ac.mips64-linux" is compiler and "gcc" is
compiler type in yaml file. In command line, It can be set as -Cc '{"gcc.cx.a.b-ac.mips64-linux":"gcc"}'

18. What is debug mode?

Setting `debug: True` sends all the files we found to all matching types. By default, it will only send files not
detected by package manager to BDBA and Signature matching.

19. How to run a specific matching type?

You can select modes: sig, bdba, pkg_mgr in config file to run specific ones.

20. I already have run blackduck-c-cpp once. I ran in offline mode. I want to run in online mode. Do I need to do the
    full build again?

No, you can set `use_offline_files: True` and `skip_build: True` to use already stored files and just upload it to Black
Duck.

21. I already have run blackduck-c-cpp once. I got a few errors after build is finished which are fixed now. I want to
    run again. Do I need to do the full build again?

No, you can set `skip_build: True` to skip build process.

22. How to exclude full directory in signature scan method?
    signature scanning files are all placed under ..\sig_scan\sig_files\ directory.
    Example: C:\Users\kakarlas\.blackduck\blackduck-c-cpp\output\godot-windows-jul11-2\sig_scan\sig_files\
    It has below paths in sig_files folder:
    C:\Users\kakarlas\.blackduck\blackduck-c-cpp\output\godot-windows-jul11-2\sig_scan\sig_files\Users\
    C:\Users\kakarlas\.blackduck\blackduck-c-cpp\output\godot-windows-jul11-2\sig_scan\sig_files\Program/ Files\
    C:\Users\kakarlas\.blackduck\blackduck-c-cpp\output\godot-windows-jul11-2\sig_scan\sig_files\godot\
    Pass this in excludes.txt:
    /Users/
    /Program\ Files/
    In yaml file: add below command:
    additional_sig_scan_args: '--snippet-matching --exclude-from C:\Users\kakarlas\Desktop\excludes.txt'

23. should it be additional_sig_scan_args: '--individualFileMatching=BINARY' when want to use "Binary" value for
    individualFileMatching?
    individualFileMatching is turned on by default on blackduck-c-cpp tool and can't be turned off.

24. bdio splitter fails to split one part when uploading to hub. How to fix it?
    Splitter operates on the node numbers, not size, so when a dataset contains large archives, it performs suboptimally.
    There are parameters to tweak it - bdio_split_max_file_entries and bdio_split_max_chunk_nodes. 
    bdio_split_max_file_entries= 100000 and bdio_split_max_chunk_nodes=3000 by default. 
    If default values don't work, try reducing bdio_split_max_file_entries to about 80000 and see if the file size drops closer to 5GB.
    

