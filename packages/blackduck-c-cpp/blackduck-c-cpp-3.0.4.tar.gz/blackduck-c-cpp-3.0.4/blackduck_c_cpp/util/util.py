"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import subprocess
import logging
import os
import sys
import glob
from chardet.universaldetector import UniversalDetector
import tqdm
import zipfile

'''
Utility class to keep commonly used methods/functionality here
'''


def conf_cmd(spec, cov_bin, cov_conf):
    try:
        cov_configure_path = glob.glob(os.path.join(cov_bin, 'cov-configure*'))[0]
    except IndexError:
        error_and_exit.error("cov-configure not found in bin directory at location: {}".format(cov_bin))
    return '"{}" -c "{}" {}'.format(cov_configure_path, os.path.join(cov_conf, "bld.xml"), spec)


def run_cmd(cmd, curdir=None, suppress_output=False, env=None):
    logging.debug("command to run in run_cmd {}".format(cmd))
    if env and curdir:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True,
                                   cwd=curdir)
    elif env:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    elif curdir:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=curdir)
    else:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        try:
            realtime_output = process.stdout.readline().decode(sys.getdefaultencoding())
            if realtime_output == '' and process.poll() is not None:
                break
            if realtime_output:
                try:
                    if not suppress_output:
                        logging.info(realtime_output.strip())
                    if suppress_output:
                        logging.debug(realtime_output.strip())
                except UnicodeEncodeError:
                    logging.warning("UnicodeEncodeError Exception occurred: skipping a line")
                except UnicodeDecodeError:
                    logging.warning("UnicodeDecodeError Exception occurred: skipping a line")
        except UnicodeEncodeError:
            logging.warning("UnicodeEncodeError Exception occurred: skipping a line")
        except UnicodeDecodeError:
            logging.warning("UnicodeDecodeError Exception occurred: skipping a line")
    return process.returncode


def run_cmd_emit(cmd):
    logging.debug("command to run in run_cmd_emit {}".format(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                       encoding=sys.getdefaultencoding(), errors='replace')
    return p.stdout.replace(os.linesep, '\n').split('\n')


def value_getstatusoutput(output):
    status = False
    if output[0] == 0:  ## success
        status = True
        return status, output[1]
    else:  ## failed
        return status, "no path found matching pattern"


def get_absolute_path(relative_path):
    try:
        absolute_path = os.path.abspath(relative_path)
        if absolute_path != relative_path:
            logging.warning(
                "{} appears to be a relative path. Using extracted absolute path {} instead.".format(relative_path,
                                                                                                     absolute_path))
        return absolute_path
    except:
        logging.error(
            "Could not get absolute path for {}. Will attempt to proceed with relative path.".format(relative_path))
        return relative_path


def resolve_path(path):
    """
    Function to resolve a path that contains "../" segments
    For example /lib/a/b/../c -> /lib/a/c.
    param: (string) path
    return: (string) resolved path
    """
    new_path = []
    for component in path.split('/'):
        if len(component) > 0:
            if component == '..':
                new_path = new_path[0:len(new_path) - 1]
            else:
                new_path = new_path + [component]
    return '/' + '/'.join(new_path)


def get_encoding(file_path):
    try:
        detector = UniversalDetector()
        with open(file_path, 'rb') as file:
            for line in file:
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        return detector.result['encoding']
    except:
        logging.warning("Encoding in file could not be automatically detected, will use system default")
    return sys.getdefaultencoding()


def get_dir_size(dir):
    size = 0
    for path, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(path, file)
            size += os.path.getsize(file_path)
    return size


def zip_files(files_to_zip, zip_output_path):
    if os.path.exists(zip_output_path):
        os.remove(zip_output_path)
    logging.debug("using zipfile module")

    with zipfile.ZipFile(zip_output_path, 'w', compression=zipfile.ZIP_DEFLATED, strict_timestamps=False) as zip_object:
        with tqdm.tqdm(total=len(files_to_zip)) as bar:
            for file_path in files_to_zip:
                try:
                    path = os.path.realpath(file_path)
                    zip_object.write(path, arcname=path)
                    bar.update(1)
                except FileNotFoundError:
                    logging.debug("file not found {}".format(path))
                    pass
                except IndexError:
                    logging.debug("index error for zip {}".format(path))
                    pass



def upload_scan(filename, hub, bd_url):
    url = bd_url + "/api/scan/data/?mode=replace"
    headers = dict()
    if filename.endswith('.json') or filename.endswith('.jsonld'):
        headers['Content-Type'] = 'application/ld+json'
        with open(filename, "rb") as f:
            response = hub.session.post(url, headers=headers, data=f)
    elif filename.endswith('.bdio'):
        headers['Content-Type'] = 'application/vnd.blackducksoftware.bdio+zip'
        with open(filename, "rb") as f:
            response = hub.session.post(url, headers=headers, data=f)
    else:
        raise Exception("Unkown file type")
    return response


def error_and_exit(message):
    logging.error(message)
    sys.exit(1)

def print_error(message):
    logging.error(message)

