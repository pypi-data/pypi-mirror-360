"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""
import requests.exceptions
from blackduck import Client as HubClient
from blackduck_c_cpp.util import util
from requests.exceptions import ConnectionError


class HubAPI:

    def __init__(self, bd_url, api_token, insecure):
        self.bd_url = bd_url
        self.api_token = api_token
        self.insecure = insecure
        self.hub = None
        try:
            self.hub = HubClient(base_url=self.bd_url, token=self.api_token, verify=(not self.insecure), timeout=600)
        except KeyError:
            util.error_and_exit("Make sure you have the right API key and --insecure flag is set correctly")
        except ConnectionError:
            util.error_and_exit(
                "ConnectionError occurred. Make sure you have the correct url and insecure flag is set correctly")

    def create_or_verify_project_version_exists(self, project_name, version_name, project_group_name, project_description,
                                                phase='DEVELOPMENT'):
        try:
            project = self.get_project_by_name(project_name)
            if project:
                version = self.get_version_by_name(project, version_name)
                if version:
                    return
                if not version:
                    response = self.create_project_version(project, version_name, parameters={'phase': phase})
            else:
                project_group_url = self.get_project_group_url_by_name(project_group_name)
                if project_group_url:
                    response = self.create_project(project_name, version_name, parameters={'version_phase': phase,
                                                                                           'projectGroup': project_group_url,
                                                                                           'description': project_description})
                else:
                    response = self.create_project(project_name, version_name, parameters={'version_phase': phase, 'description': project_description})
        except requests.exceptions.SSLError:
            util.error_and_exit(
                "SSLError occurred. Make sure you have the correct url and insecure flag is set correctly")
        except RuntimeError:
            util.error_and_exit(
                "Make sure you have the right API key and --insecure flag is set correctly")

    def create_project(self, project_name, version_name="Default Version", parameters={}):

        url = self.hub.list_resources()['projects']
        post_data = {
            "name": project_name,
            "description": parameters.get("description", ""),
            "projectTier": parameters.get("project_tier", ""),
            "projectOwner": parameters.get("project_owner", ""),
            "projectLevelAdjustments": parameters.get("project_level_adjustments", True),
            "cloneCategories": [
                "COMPONENT_DATA",
                "VULN_DATA"
            ],
            "versionRequest": {
                "phase": parameters.get("version_phase", "PLANNING"),
                "distribution": parameters.get("version_distribution", "EXTERNAL"),
                "projectLevelAdjustments": parameters.get("project_level_adjustments", True),
                "versionName": version_name
            },
            "projectGroup": parameters.get("projectGroup", "")
        }
        r = self.hub.session.post(url, json=post_data)
        if r.status_code == 201:
            pass  ##created project
        else:
            self.hub.http_error_handler(r)
            util.error_and_exit(
                "Error creating project -- (Response({}): {})".format(r.status_code, r.text))

    # create new version for project
    def create_project_version(self, project, version_name, parameters={}):
        url = self.get_link(project, "versions")
        post_data = {
            "versionUrl": url,
            "cloneCategories": [
                "VULN_DATA",
                "COMPONENT_DATA"
            ],
            "versionName": version_name,
            "phase": parameters['phase'],
            "distribution": parameters.get("distribution", "EXTERNAL")
        }
        r = self.hub.session.post(url, json=post_data)
        if r.status_code == 201:
            print("created version {}".format(version_name))
        else:
            self.hub.http_error_handler(r)
            util.error_and_exit(
                "Error creating project version-- (Response({}): {})".format(r.status_code, r.text))

    def get_project_by_name(self, project_name):
        project_list = self.hub.get_resource('projects', params={"q": "name:{}".format(project_name)})
        for project in project_list:
            if project['name'] == project_name:
                return project

    ## get version for specific project
    def get_version_by_name(self, project, version_name):
        version_list = self.hub.get_resource('versions', project)
        for version in version_list:
            if version['versionName'] == version_name:
                return version

    ## get project_group_url for given project_group_name
    def get_project_group_url_by_name(self, project_group_name):
        projects_group_list = self.hub.get_json("/api/project-groups/?limit=9999")
        for project_group in projects_group_list['items']:
            if project_group['name'] == project_group_name:
                return project_group['_meta']['href']

    def get_link(self, bd_rest_obj, link_name):
        # returns the URL for the link_name OR None
        if bd_rest_obj and '_meta' in bd_rest_obj and 'links' in bd_rest_obj['_meta']:
            for link_obj in bd_rest_obj['_meta']['links']:
                if 'rel' in link_obj and link_obj['rel'] == link_name:
                    return link_obj.get('href', None)

    def get_hub_version(self):
        hub_version_dict = {}
        try:
            hub_version_dict = self.hub.get_json("/api/current-version")
        except RuntimeError:
            util.error_and_exit("Make sure you have the right API key and --insecure flag is set correctly")
        except Exception as e:  # in case we don't get version info
            util.print_error("WARNING: /api/current-version returned no version with exception - {}".format(e))
            hub_version_dict['version'] = '0.0.0'
        return hub_version_dict['version']

    def get_latest_scan_cli_version(self):
        url = '{}/api/tools/scan.cli.zip/versions/latest/platforms/linux'.format(self.bd_url)
        response = self.hub.session.head(url)
        if response.ok:
            return response.headers.get('Version')
        return None
