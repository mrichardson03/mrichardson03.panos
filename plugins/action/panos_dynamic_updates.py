# Copyright 2020 Palo Alto Networks, Inc
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# pylint: skip-file

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time
import xml.etree.ElementTree

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionBase):

    # local copy of task vars passed into this action module
    local_task_vars = {}

    def __execute_op(self, cmd):
        """
        Local method to execute the panos_op module and return parsed results

        :param cmd: op cmd in xml format to execute
        :return: parsed module return value
        """
        module_args = {"cmd": cmd, "cmd_is_xml": True}

        op_results = self._execute_module(
            module_name="panos_op",
            module_args=module_args,
            task_vars=self.local_task_vars,
        )

        op_xml = op_results["stdout_xml"]
        return xml.etree.ElementTree.fromstring(op_xml)

    def __wait_for_job(self, job_id):
        """
        Polls for job completion.

        :param job_id: ID of job to poll for.
        """
        cmd = "<show><jobs><id>{0}</id></jobs></show>".format(job_id)

        display.vvvv("poll_for_job(): job_id = {0}, interval = {1}".format(job_id, 5))

        while True:
            result = self.__execute_op(cmd)
            status = result.find("./result/job/status")

            if status is None:
                raise AnsibleActionFail("Could not find status element in job.")

            display.vvvv(
                "poll_for_job(): job_id {0} status = {1}".format(job_id, status.text)
            )

            if status.text == "FIN":
                return result
            else:
                time.sleep(5)

    def __get_latest_version_for_content_type(self, content_type):
        """
        Iterate through all available content of the specified type, locate and return the version with the highest
        version number. If that version is already installed, return None as no further action is necessary

        :param content_type: type of content to check
        :return: version-number to download and install or None if already at the latest
        """
        latest_version = ""
        latest_version_first = 0
        latest_version_second = 0
        latest_version_current = "no"

        cmd = "<request><{0}><upgrade><check/></upgrade></{0}></request>".format(
            content_type
        )
        op_doc = self.__execute_op(cmd)

        for entry in op_doc.findall(".//entry"):
            version = entry.find("./version").text
            current = entry.find("./current").text
            # version will have the format 1234-1234
            version_parts = version.split("-")
            version_first = int(version_parts[0])
            version_second = int(version_parts[1])

            if (
                version_first > latest_version_first
                and version_second > latest_version_second
            ):
                latest_version = version
                latest_version_first = version_first
                latest_version_second = version_second
                latest_version_current = current

        if latest_version_current == "yes":
            return None

        else:
            return latest_version

    def run(self, tmp=None, task_vars=None):

        self.local_task_vars = task_vars

        # run default action module first
        result = super(ActionModule, self).run(tmp, task_vars)

        content_type = self._task.args.get("content_type", "content")

        display.v("Checking for latest version of type: {0}".format(content_type))
        latest_version = self.__get_latest_version_for_content_type(content_type)

        if latest_version is None:
            display.v("Latest version of {0} is already installed".format(content_type))
            # return here changed = False
            result["changed"] = False
            return result

        display.v("Downloading Dynamic Update for type: {0}".format(content_type))
        cmd = (
            "<request>"
            "<{0}><upgrade><download><latest/></download></upgrade></{0}>"
            "</request>".format(content_type)
        )

        op_result = self.__execute_op(cmd)
        job_element = op_result.find(".//job")

        job_id = job_element.text

        self.__wait_for_job(job_id)

        display.v("Installing Dynamic Update for type: {0}".format(content_type))
        install_cmd = (
            "<request><{0}><upgrade><install>"
            "<version>latest</version><commit>no</commit>"
            "</install></upgrade></{0}></request>".format(content_type)
        )

        install_result = self.__execute_op(install_cmd)
        job_element = install_result.find(".//job")

        job_id = job_element.text

        self.__wait_for_job(job_id)

        result["changed"] = True

        return result
