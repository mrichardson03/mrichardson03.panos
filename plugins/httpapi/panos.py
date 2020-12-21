# -*- coding: utf-8 -*-

#  Copyright 2020 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
author:
    - Michael Richardson (@mrichardson03)
httpapi : panos
short_description: HttpApi plugin for PAN-OS devices
description:
    - HttpApi plugin for PAN-OS devices
version_added: '1.0.0'
options:
    api_key:
        type: str
        description:
            - Use API key for authentication instead of username and password
        vars:
            - name: ansible_api_key
"""

import json
import time
import xml.etree.ElementTree

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.basic import to_text
from ansible.module_utils.six.moves import urllib
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.plugins.httpapi import HttpApiBase
from ansible.utils.display import Display
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAPIError,
    UnauthorizedError,
    cmd_xml,
)

display = Display()

XML_BASE_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
}

JSON_BASE_HEADERS = {"Content-Type": "application/json"}


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        super().__init__(connection)

        self._api_key = None
        self._device_info = None

    def login(self, username=None, password=None):
        """
        Handle PAN-OS API authentication.

        Plugin can use an optional API key.  If it is provided, the plugin will
        store it for further calls.

        If an API key is not provided, one will be generated using the given
        username and password, and stored for further calls.

        :param username: Username used for API key generation.
        :param password: Password used for API key generation.
        """

        api_key = self.get_option("api_key")

        display.vvvv("login(): start")

        # If API key was given as an option, store for further use.
        if api_key:
            self._api_key = api_key
        else:
            if not username and not password:
                raise AnsibleConnectionFailure("Username and password are required")
            else:
                # If API key was not specified, generate one and store it.
                key = self.keygen(username, password)
                display.vvvv("storing api key = {0}".format(key))
                self._api_key = key

        # Refresh device info after successful login.
        if self._api_key is not None:
            self.version()
        else:
            raise AnsibleConnectionFailure("Invalid credential")

        display.vvvv("login(): complete")

    def api_key(self):
        """ Return the API key used by this connection. """
        return self._api_key

    def keygen(self, username, password):
        """
        Generates an API key for the requested user.  If successful, this key
        can be used later as a URL encoded parameter 'key', or in the
        'X-PAN-KEY' header (PAN-OS 9.0+).

        :param username: Username used to generate API key.
        :param password: Password used to generate API key.
        :returns: String containing API key.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/get-started-with-the-pan-os-xml-api/get-your-api-key.html
        """
        params = {"type": "keygen", "user": username, "password": password}
        code, data = self.send_request({}, params=params, headers=XML_BASE_HEADERS)

        root = xml.etree.ElementTree.fromstring(data)
        key = root.find("./result/key")

        if key is not None:
            return key.text
        else:
            return None

    def show(self, xpath=None):
        """
        Retrieves the running configuration from the device.

        :param xpath: Retrieve a specific portion of the configuration.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/get-active-configuration/use-xpath-to-get-active-configuration.html
        """
        pass

    def get(self, xpath=None):
        """
        Performs the 'get' API request.  This is used to retrieve the candidate
        configuration from the device.

        :param xpath: Retrieve a specific portion of the configuration.
        :returns: String containing XML response.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/get-candidate-configuration.html
        """
        params = {"type": "config", "key": self._api_key, "action": "get"}

        if xpath:
            params.update({"xpath": xpath})

        code, data = self.send_request({}, params=params)
        return data

    def set(self, xpath, element):
        """
        Creates a new object at a specified location in the configuration.

        :param xpath: Location of the new object.
        :param element: Object to add.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/set-configuration.html
        """

        params = {
            "type": "config",
            "key": self._api_key,
            "action": "set",
            "xpath": xpath,
            "element": element,
        }

        data = urllib.parse.urlencode(params)
        code, response = self.send_request(data)

        return self._validate_response(code, response)

    def edit(self, xpath, element):
        """
        Replaces an existing object with a new value.

        Commonly used after retrieving the existing value using 'show'.

        :param xpath: Location of the object.
        :param element: New value of object.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/edit-configuration.html
        """
        params = {
            "type": "config",
            "key": self._api_key,
            "action": "edit",
            "xpath": xpath,
            "element": element,
        }

        data = urllib.parse.urlencode(params)
        code, response = self.send_request(data)

        return self._validate_response(code, response)

    def delete(self, xpath):
        """
        Deletes an object from the configuration.

        :param xpath: Location of the object.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/delete-configuration.html
        """
        pass

    def rename(self, xpath, newname):
        """
        Renames an object in the configuration.

        :param xpath: Location of the object.
        :param newname: New name for object.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/rename-configuration.html
        """
        pass

    def move(self, xpath, where, dst=None):
        """
        Moves the location of an existing object.

        :param xpath: Location of the object.
        :param where: Can be 'before', 'after', 'top', or 'bottom'.
        :param dst:   Destination XPath.  Used when 'where' is 'before' or 'after'.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/move-configuration.html
        """
        pass

    def override(self, xpath, element):
        """
        Overrides a setting that has been pushed to a firewall from a template.

        :param xpath: Location of the object.
        :param element: New value of the object.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/configuration-api/override-configuration.html
        """
        pass

    def commit(
        self,
        force=False,
        partial=False,
        exclude_device_and_network=False,
        exclude_shared_object=False,
        admins=None,
        description=None,
    ):
        """
        Commits the candidate configuration to the device.

        :param validate: Validate configuration - do not actually commit.
        :param force: Perform a force commit.
        :param partial: Perform a partial commit.
        :param exclude_device_and_network: Exclude device and network configuration
        from a partial commit.
        :param exclude_shared_objects: Exclude shared objects from a partial commit.
        :param admins: Only commit changes from certain administrators.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api/commit.html
        """
        cmd = "commit"

        if description:
            cmd += " description '{0}'".format(description)

        params = {"type": "commit", "key": self._api_key, "cmd": cmd_xml(cmd)}

        code, data = self.send_request({}, params=params)

        return data

    def commit_all(self, validate=False, device_groups=None, vsys=None, serials=None):
        """
        Validate and push shared policies from a Panorama device.

        :param validate: Validate configuration - do not actually push.
        :param device_groups: Commit to specific device groups.
        :param vsys: Commit to specific virtual system.
        :param serials: Commit to specific firewall serial numbers.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api/commit-all.html
        """
        pass

    def op(self, cmd, is_xml=False):
        """
        Runs an operational command.

        :param cmd: Command to run.
        :param is_xml: Command is in XML format.
        :returns: Tuple containing HTTP code and response data.

        Reference:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/pan-os-xml-api-request-types/run-operational-mode-commands-api.html
        """
        params = {
            "type": "op",
            "key": self._api_key,
            "cmd": cmd if is_xml else cmd_xml(cmd),
        }

        code, data = self.send_request({}, params=params)
        return data

    # reports
    # export
    # import
    # log
    # user-id

    def version(self):
        """
        Runs the version API command.

        Retrieves device software version, vsys mode, model, and serial number.

        :returns: Dict containing device info.
        """
        if self._device_info:
            return self._device_info

        params = {"type": "version", "key": self._api_key}
        code, data = self.send_request({}, params=params)

        root = xml.etree.ElementTree.fromstring(data)
        result = root.find("./result")

        self._device_info = {}
        self._device_info.update(
            {
                "sw-version": result.findtext("sw-version"),
                "multi-vsys": result.findtext("multi-vsys"),
                "model": result.findtext("model"),
                "serial": result.findtext("serial"),
            }
        )

        display.vvvv("version = {0}".format(self._device_info))

        return self._device_info

    def poll_for_job(self, job_id, interval=5):
        """
        Polls for job completion.

        :param job_id: ID of job to poll for.
        :param interval: Poll interval, in seconds.
        """
        cmd = "<show><jobs><id>{0}</id></jobs></show>".format(job_id)

        display.vvvv(
            "poll_for_job(): job_id = {0}, interval = {1}".format(job_id, interval)
        )

        while True:
            result = self.op(cmd, is_xml=True)

            root = xml.etree.ElementTree.fromstring(result)
            status = root.find("./result/job/status")

            if status is None:
                raise AnsibleConnectionFailure("Could not find status element in job.")

            display.vvvv(
                "poll_for_job(): job_id {0} status = {1}".format(job_id, status.text)
            )

            if status.text == "FIN":
                return result
            else:
                time.sleep(interval)

    def is_panorama(self):
        """
        Returns if the connected device is a Panorama instance.

        :returns: Boolean if this device is a Panorama or not.
        """
        return True if self._device_info["model"] == "Panorama" else False

    def update_auth(self, response, response_text):
        """
        Returns the per-request auth token.  For PAN-OS 9.0+, this is the
        header 'X-PAN-KEY' set to the API key.

        :returns: Dictionary with the 'X-PAN-KEY' set if the connection is
        established, None if not.
        """
        if self._api_key:
            return {"X-PAN-KEY": self._api_key}
        else:
            return None

    def send_request(
        self,
        data=None,
        path="/api/",
        params=None,
        method="POST",
        headers=None,
        request_type="xml",
        **message_kwargs,
    ):
        """
        Sends a request to the PAN-OS API.

        :param data: Data to send to the API endpoint.
        :param path: URL path used for the API endpoint.
        :param params: Parameters to send with request (will be URL encoded).
        :param method: HTTP method to for request.
        :param headers: HTTP headers to include in request.
        :param request_type: API request type ('xml' or 'json')
        :returns: Tuple (HTTP response code, data object).

        Error Codes:
        https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-panorama-api/get-started-with-the-pan-os-xml-api/pan-os-xml-api-error-codes.html
        """

        if params is not None:
            params = urllib.parse.urlencode(params) if params else ""
            path += "?{0}".format(params)

        if data is None:
            data = {}

        if headers is None:
            headers = {}

        if request_type == "xml":
            headers.update(
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Content-Length": len(data),
                }
            )
        else:
            data = json.dumps(data)

            headers.update(
                {"Content-Type": "application/json", "Content-Length": len(data)}
            )

        display.vvvv("send_request(): headers = {0}".format(headers))
        display.vvvv("send_request(): method = {0}".format(method))
        display.vvvv("send_request(): path = {0}".format(path))
        display.vvvv("send_request(): data = {0}".format(data))

        try:
            response, response_data = self.connection.send(
                path, data, method=method, headers=headers
            )

            return response.getcode(), self._handle_response(
                response_data, request_type=request_type
            )
        except HTTPError as e:
            return e.code, e.read()

    def handle_httperror(self, exc):

        if exc.code == 401:
            if self.connection._auth:
                # Stored auth appears to be invalid, clear and retry.
                self.connection._auth = None
                self.login(
                    self.connection.get_option("remote_user"),
                    self.connection.get_option("password"),
                )
                return True
            else:
                # Unauthorized and there's no token.  Return an error.
                return False

        elif exc.code == 404:
            return False

        return exc

    @staticmethod
    def _handle_response(data, request_type="xml"):
        data = to_text(data.getvalue())

        display.vvvv("_handle_response(): response = {0}".format(data))

        if request_type == "xml":
            return data
        else:
            try:
                return json.loads(data) if data else {}
            except ValueError:
                return data

    @staticmethod
    def _validate_response(code, response):

        if code == 403:
            raise UnauthorizedError("Unauthorized Request to PAN-OS API")

        if code != 200:
            raise ConnectionError("Error Connecting to PAN-OS API!")

        data = to_text(response)
        root = xml.etree.ElementTree.fromstring(data)

        if "status" not in root.attrib or "code" not in root.attrib:
            raise PanOSAPIError("Unknown Response from PAN-OS API")

        status = root.attrib["status"]
        api_code = root.attrib["code"]

        if status != "success":
            raise PanOSAPIError(
                "API Call status was not found or not successful: {0}".format(api_code)
            )

        if api_code == "16":
            raise UnauthorizedError("API Call was unauthorized")

        if api_code not in ["19", "20"]:
            raise PanOSAPIError("API Call was not successful: {0}".format(api_code))

        # FIXME - Should we unwrap the response/result here for ease of use for all calling modules?
        return data
