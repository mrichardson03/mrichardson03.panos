# Copyright 2021 Palo Alto Networks, Inc
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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import xml.etree.ElementTree

import xmltodict
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(["content_type"])

    def _get_latest_content_version(self, content_type):
        latest_version = ""
        latest_version_first = 0
        latest_version_second = 0
        latest_version_current = "no"

        cmd = "<request><{0}><upgrade><check/></upgrade></{0}></request>".format(
            content_type
        )
        op_xml = self._connection.op(cmd=cmd, is_xml=True)
        op_doc = xml.etree.ElementTree.fromstring(op_xml)

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

    def _download_install_content(self, content_type):
        download = (
            "<request>"
            "<{0}><upgrade><download><latest/></download></upgrade></{0}>"
            "</request>".format(content_type)
        )

        self._connection.submit_and_poll_for_job(download)

        install = (
            "<request><{0}><upgrade><install>"
            "<version>latest</version><commit>no</commit>"
            "</install></upgrade></{0}></request>".format(content_type)
        )

        self._connection.submit_and_poll_for_job(install)

    def _fetch_licenses(self):
        """ Retrieves info on licensees. """
        cmd = "request license info"

        try:
            result = self._connection.op(cmd)
        except Exception as e:
            raise AnsibleError("Error retreiving license info.") from e

        parsed = xmltodict.parse(result, force_list=("entry,"))
        licenses = parsed.get("response").get("result").get("licenses", None)

        if licenses is None:
            return []
        else:
            return parsed.get("response").get("result").get("licenses").get("entry", [])

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super().run(tmp, task_vars)
        del tmp

        content_type = self._task.args.get("content_type", None)

        if content_type is not None:
            if content_type not in ["content", "anti-virus", "wildfire"]:
                raise AnsibleError(
                    "'content_type' must be one of 'content', 'anti-virus', 'wildfire'"
                )

            latest_version = self._get_latest_content_version(content_type)

            if latest_version is not None:
                self._download_install_content(content_type)
                result["changed"] = True
                result[content_type] = latest_version

        else:
            license_result = self._fetch_licenses()
            content_types = []

            for lic in license_result:
                if "Threat" in lic["feature"]:
                    content_types.append("content")
                    content_types.append("anti-virus")
                elif "WildFire" in lic["feature"]:
                    content_types.append("wildfire")

            for content_type in content_types:
                latest_version = self._get_latest_content_version(content_type)

                if latest_version is not None:
                    self._download_install_content(content_type)
                    result["changed"] = True
                    result[content_type] = latest_version

        return result
