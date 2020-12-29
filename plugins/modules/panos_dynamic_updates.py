#!/usr/bin/python

#  Copyright 2020 Palo Alto Networks, Inc
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

DOCUMENTATION = """
---
module: panos_dynamic_updates
short_description: Installs dynamic updates of the specified type.
description:
    - This module will allow the user to install the latest version of the dynamic content type.
    - Depending on the many factors, the installation of dynamic updates can take
      to complete. It is recommended to either wait in playbooks for an appropriate amount of time,
      or adjust the Ansible persistent connection timeout using the
      `ANSIBLE_PERSISTENT_CONNECT_TIMEOUT` env var (or similar setting
      in `ansible.cfg`) and use the `timeout` parameter
      as in the example.
    - See the Ansible Network Debug and Troubleshooting Guide for more
      information.
author:
    - 'Nathan Embery (@nembery)'
version_added: '1.0.0'
requirements: []

notes:
    - Checkmode is supported.
    - Panorama is supported.
options:
    content_type:
        description:
            - The type of dynamic update to request. Valid options are 'content', 'wildfire' and 'anti-virus'.
        type: str
        default: content
        choices:
            - content
            - anti-virus
            - wildfire
        required: false
"""

EXAMPLES = """
- name: Install Latest Dynamic Content Updates
  panos_dynamic_updates:
    content_type: content
  timeout: 180

- name: Install Latest Dynamic anti-virus Updates
  panos_dynamic_updates:
    content_type: anti-virus
  timeout: 180

"""

RETURN = """
changed:
    description: A boolean value indicating if the task made any changes.
    returned: always
    type: bool
"""

import xml.etree.ElementTree

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)

try:
    import xmltodict

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def __execute_op(module, cmd):
    op_xml = module.connection.op(cmd=cmd, is_xml=True)
    return xml.etree.ElementTree.fromstring(op_xml)


def __get_latest_version_for_content_type(module, content_type):
    """
    Iterate through all available content of the specified type, locate and return the version with the highest
    version number. If that version is already installed, return None as no further action is necessary

    :param module: this ansible module
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
    op_xml = module.connection.op(cmd=cmd, is_xml=True)
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


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            content_type=dict(
                required=False,
                type="str",
                choices=("content", "anti-virus", "wildfire"),
                default="content",
            )
        ),
        supports_check_mode=True,
    )

    if not HAS_LIB:
        module.fail_json(msg="Missing required libraries.")

    try:
        content_type = module.params["content_type"]

        latest_version = __get_latest_version_for_content_type(module, content_type)

        if latest_version is None:
            # return here changed = False
            module.exit_json(changed=False)

        if module.check_mode:
            module.exit_json(changed=True)

        cmd = (
            "<request>"
            "<{0}><upgrade><download><latest/></download></upgrade></{0}>"
            "</request>".format(content_type)
        )

        op_result = __execute_op(module, cmd)
        job_element = op_result.find(".//job")

        job_id = job_element.text

        module.connection.poll_for_job(job_id)

        install_cmd = (
            "<request><{0}><upgrade><install>"
            "<version>latest</version><commit>no</commit>"
            "</install></upgrade></{0}></request>".format(content_type)
        )

        install_result = __execute_op(module, install_cmd)
        job_element = install_result.find(".//job")

        job_id = job_element.text

        module.connection.poll_for_job(job_id)

        module.exit_json(changed=True)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
