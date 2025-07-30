"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""
from google.cloud import storage
from google.oauth2 import service_account
import hashlib
import shutil
import logging
import json
from blackduck_c_cpp.util import util
import os
import stat
import tempfile
from blackduck_c_cpp.util import global_settings
import zipfile


class CoverityInstall:
    """Class to download latest coverity package for different OS """

    def __init__(self, cov_home, hub_api, platform, force, blackduck_c_cpp_version):
        self.hub_api = hub_api
        self.hub = hub_api.hub
        self.cov_home = cov_home
        self.platform = platform
        if self.platform == global_settings.darwin_pltfrm:
            self.platform = global_settings.macos_pltfrm
            platform = global_settings.macos_pltfrm
        self.force = force
        self.cov_zippath = 'cov-latest' + '-' + platform + '.zip'
        self.cov_filepath = os.path.join(self.cov_home, self.cov_zippath)
        self.tool_token_response = None
        self.tool_token_json = None
        self.gcp_filepath = None
        self.blackduck_c_cpp_version = blackduck_c_cpp_version
        self.min_cov_year_for_api = 2021
        self.min_cov_vers_for_api = 10
        try:
            self.run()
        except Exception as e:
            logging.error("Exception occurred: {}".format(e))

    def hub_api_tool_token(self):
        """
        get token from hub tool-token api
        """
        data = {"clientName": self.platform, "clientVersion": self.blackduck_c_cpp_version}
        self.tool_token_response = self.hub.session.post('{}/api/tool-token'.format(self.hub_api.bd_url),
                                                         json=data)
        if not self.tool_token_response.ok:
            logging.error(
                "Problem connecting to /api/tool-token -- (Response({}): {})".format(
                    self.tool_token_response.status_code,
                    self.tool_token_response.text))
        self.tool_token_json = self.tool_token_response.json()

    def find_any_coverity_version(self):
        """check if any version of coverity is present"""
        if os.path.exists(self.cov_filepath):
            logging.debug(
                "Using older coverity version already present on the system from {}".format(
                    self.cov_filepath))
        else:
            util.error_and_exit("No coverity version is present on the system. Please contact Black Duck Support")

    def gcp_download(self):
        """
        Download mini coverity package from gcp if credentials are correct
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tempfile_path = os.path.join(tmpdir, self.cov_zippath)
            try:
                storage_credentials = service_account.Credentials.from_service_account_info(
                    self.tool_token_json['jsonWebToken'])
                client = storage.Client(credentials=storage_credentials)
                gcp_path_split = self.gcp_filepath.split("/")
                object_name = gcp_path_split[-1]
                bucket_name = gcp_path_split[-2]
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(object_name)
                logging.info("Downloading coverity latest version from gcp to {}".format(tempfile_path))
                blob.download_to_filename(tempfile_path)
            except Exception as e:
                logging.warning("unable to connect to gcp - {}".format(e))
                self.find_any_coverity_version()
                return
            if not self.gcp_checksum == hashlib.sha256(open(tempfile_path, 'rb').read()).hexdigest():
                if not self.force:
                    logging.error(
                        "There's a mismatch between api tool token and gcp checksums, If you want to continue with previous version of coverity, please set force to True in yaml file and retry")
                    util.error_and_exit(
                        "PLEASE CONTACT BLACK DUCK SUPPORT IMMEDIATELY: Mismatch between GCP Bucket and Tool Token Sha2.")
                else:
                    self.find_any_coverity_version()
            else:
                if not zipfile.is_zipfile(tempfile_path):
                    logging.error("Downloaded file is not a valid zip file: {}, please contact blackduck support".format(tempfile_path))
                    util.error_and_exit("Invalid coverity zip file downloaded from GCP")

                # at this point, self.cov_home should be empty - can have data due to migration from .synopsys to .blackduck dir
                if os.path.exists(self.cov_home):
                    logging.debug("Removing old coverity home directory at {}".format(self.cov_home))
                    shutil.rmtree(self.cov_home)

                if os.path.exists(self.cov_filepath):
                    os.remove(self.cov_filepath)
                    logging.debug("Removing old coverity zip file at {}".format(self.cov_filepath))
                # create cov_filepath parent directory
                os.makedirs(os.path.dirname(self.cov_filepath), exist_ok=True)
                dest = shutil.move(tempfile_path, self.cov_filepath)
                logging.debug("moving coverity files from {} to {}".format(tempfile_path, dest))
                self.unzip_downloaded()

    def unzip_with_symlinks(self, zip_path, extract_dir):
        """
        Unzip a zip file, preserving symlinks (which are not handled by shutil.unpack_archive).
        """
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                extracted_path = os.path.join(extract_dir, info.filename)
                perms = info.external_attr >> 16 # to get permissions
                is_symlink = (info.external_attr >> 28) == 0xA # check if it is symlink
                if info.is_dir():
                    os.makedirs(extracted_path, exist_ok=True)
                elif is_symlink:
                    # Read the link target from the file contents
                    link_target = zf.read(info.filename).decode('utf-8')
                    os.symlink(link_target, extracted_path)
                else:
                    os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
                    with open(extracted_path, 'wb') as f:
                        f.write(zf.read(info.filename))
                    if perms:
                        os.chmod(extracted_path, perms)

    def unzip_downloaded(self):
        """
        unzip coverity package, preserving symlinks
        """
        logging.debug("Unzipping coverity latest version zip to location {}".format(self.cov_home))

        # try unzipping with symlinks, if it fails, use shutil.unpack_archive
        try:
            self.unzip_with_symlinks(self.cov_filepath, self.cov_home)
            logging.debug("Successfully unzipped coverity package with symlinks to {}".format(self.cov_home))
        except Exception as e:
            logging.error("Error unzipping coverity package with symlinks: {}, falling back to shutil.unpack_archive".format(e))
            # cleanup and then use shutil.unpack_archive
            if os.path.exists(self.cov_home):
                shutil.rmtree(self.cov_home)
            os.makedirs(self.cov_home, exist_ok=True)
            shutil.unpack_archive(self.cov_filepath, self.cov_home)

    def verify_checksum_match(self):
        """
        download coverity only if checksum doesn't match
        """
        self.gcp_checksum, self.gcp_filepath = self.tool_token_json['checksum'][self.platform].split(",")
        logging.debug("checksum of latest coverity file in gcp is {}".format(self.gcp_checksum))
        if os.path.exists(self.cov_filepath):
            sha2_filepath = hashlib.sha256(open(self.cov_filepath, 'rb').read()).hexdigest()
            if self.gcp_checksum == sha2_filepath:
                logging.info("Skipping downloading latest version of coverity as it already exists")
                return True
            else:
                logging.info("Downloading latest coverity package as it is not present on disk")
                return False
        else:
            return False

    def set_permissions(self):
        """ set executable permissions for coverity files"""
        logging.debug("setting executable permissions for coverity files")
        st = os.stat(self.cov_home)
        os.chmod(self.cov_home, st.st_mode | stat.S_IEXEC)
        for root, dirs, files in os.walk(self.cov_home):
            for d in dirs:
                st = os.stat(os.path.join(root, d))
                os.chmod(os.path.join(root, d), st.st_mode | stat.S_IEXEC)
            for f in files:
                st = os.stat(os.path.join(root, f))
                os.chmod(os.path.join(root, f), st.st_mode | stat.S_IEXEC)

    def run(self):
        """
        run coverity install
        """
        hub_version = self.hub_api.get_hub_version()
        vers_result = hub_version.split(".")
        if ((int(vers_result[0]) >= self.min_cov_year_for_api and int(
                vers_result[1]) >= self.min_cov_vers_for_api) or int(
                vers_result[0]) >= self.min_cov_year_for_api + 1):
            self.hub_api_tool_token()
            match_result = self.verify_checksum_match()
            if not match_result:
                self.gcp_download()
            else:
                logging.debug("Latest version is already present on the system at {}".format(self.cov_home))
            self.set_permissions()
        else:
            util.error_and_exit(
                "Automatic update of coverity not supported in Black Duck version {}. please provide coverity_root in yaml file".format(
                    hub_version))
