import os
import re
import pandas as pd
from collections import defaultdict
from blackduck_c_cpp.util import util, global_settings
import subprocess

class LdDebugParser:

    def __init__(self):
        self.pattern_transitive = re.compile(r'(?<=file=)([^ ]+)*')
        self.pattern_direct = re.compile(r'(?<=needed by )([^ ]+)*')
        self.so_pattern = global_settings.so_pattern

    def parse_ldd_output(self, ld_result):
        """
        Parse the ldd output and return a dictionary of file paths.
        """
        output_path_set = {}
        parsed_results = re.findall(r'^\s*(\S+)\s+=>(.*) \(.*\)$', ld_result, re.MULTILINE)
        for fname, path in parsed_results:
            """ storing filename: fullpath eg: a.so: g/f/d/a.so"""
            output_path_set[fname.strip()] = path.strip()
        return output_path_set

    def build_dependency_graph(self, ld_result, output_path_set):
        """
        Build a dependency graph from the `ldd` output.
        """
        row_df = [
            # tries to retrive value if present else takes default value given
            [output_path_set.setdefault(os.path.basename(res_direct.group().strip()), res_direct.group().strip()),
             output_path_set.setdefault(os.path.basename(res_transitive.group().strip()), res_transitive.group().strip())]
            for each_line in ld_result.split("\n")
            if (res_transitive := re.search(self.pattern_transitive, each_line)) and
               (res_direct := re.search(self.pattern_direct, each_line))
        ]
        dep_df = pd.DataFrame(row_df, columns=['dep', 'dep_of_dep']).dropna()
        return dep_df

    def cleanup_transitive_dependencies(self, ld_debug_dict):
        """
        Clean up transitive dependencies in the dependency dictionary.
        """
        dep_list = list(ld_debug_dict.keys())
        dep_of_dep_list = list(ld_debug_dict.values())

        for dep, dep_of_dep in ld_debug_dict.copy().items():
            if re.match(self.so_pattern, dep):
                # check if this dependency is a transitive dependency
                dep_key = None
                for idx, trans_dep in enumerate(dep_of_dep_list):
                    if dep in trans_dep:
                        dep_key = dep_list[idx]
                        break
                # If a valid parent dependency is found, merge the current dependency into it
                if dep_key and re.match(self.so_pattern, dep_key):
                    ld_debug_dict[dep_key].update(ld_debug_dict.pop(dep))

        # Return the cleaned-up dictionary
        return ld_debug_dict

    def run_ld_debug(self, executable, bld_dir):
        """
        Main function to parse `ldd` output and build the dependency graph.
        """
        ld_debug_dict = defaultdict(set)

        # Check if the executable exists
        executable_path = executable if os.path.exists(executable) else os.path.join(bld_dir, executable)
        if not os.path.exists(executable_path):
            return ld_debug_dict

        # Run the ldd command with LD_DEBUG
        out = subprocess.getstatusoutput(f"LD_DEBUG=files ldd {executable_path} 2> /dev/null")
        status, ld_result = util.value_getstatusoutput(out)
        if not status or 'no path found matching pattern' in ld_result:
            return ld_debug_dict

        # Parse the ldd output
        output_path_set = self.parse_ldd_output(ld_result)

        # Build dependency graph
        dep_df = self.build_dependency_graph(ld_result, output_path_set)

        # Populate the dependency dictionary
        for dep, dep_of_dep in zip(dep_df['dep'], dep_df['dep_of_dep']):
            ld_debug_dict[dep].add(dep_of_dep)

        # Clean up transitive dependencies
        ld_debug_dict = self.cleanup_transitive_dependencies(ld_debug_dict)

        return ld_debug_dict