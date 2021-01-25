#!/usr/bin/python

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


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_op
short_description: execute arbitrary OP commands on PANW devices (e.g. show interface all)
description:
    - This module will allow user to pass and execute any supported OP command on the PANW device.
author:
    - 'Michael Richardson (@mrichardson03)'
version_added: '1.0.0'
requirements:
    - xmltodict
notes:
    - Checkmode is NOT supported.
    - Panorama is supported.
options:
    cmd:
        description:
            - The OP command to be performed.
        type: str
        required: true
    cmd_is_xml:
        description:
            - The cmd is already given in XML format, so don't convert it.
        type: bool
        default: false
"""

EXAMPLES = """
- name: show list of all interfaces
  panos_op:
    cmd: 'show interfaces all'

- name: show system info
  panos_op:
    cmd: 'show system info'

- name: show system info as XML command
  panos_op:
    cmd: '<show><system><info/></system></show>'
    cmd_is_xml: true
"""

RETURN = """
stdout:
    description: output of the given OP command as JSON formatted string
    returned: success
    type: str
    sample: "{system: {app-release-date: 2017/05/01  15:09:12}}"
stdout_xml:
    description: output of the given OP command as an XML formatted string
    returned: success
    type: str
    sample: "<response status=success><result><system><hostname>fw2</hostname>"
"""

import json

try:
    import xmltodict

    HAS_LIB = True
except ImportError:
    HAS_LIB = False

from ansible.module_utils.connection import ConnectionError
from ansible_collections.paloaltonetworks.panos_enhanced.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            cmd=dict(required=True), cmd_is_xml=dict(default=False, type="bool")
        ),
        supports_check_mode=False,
    )

    if not HAS_LIB:
        module.fail_json(msg="Missing required libraries.")

    cmd = module.params["cmd"]
    cmd_is_xml = module.params["cmd_is_xml"]

    changed = True
    safecmd = ["diff", "show"]

    try:
        xml_output = module.connection.op(cmd, is_xml=cmd_is_xml)

        tokens = cmd.split()

        if tokens[0] in safecmd:
            changed = False

        obj_dict = xmltodict.parse(xml_output)
        json_output = json.dumps(obj_dict)

        module.exit_json(changed=changed, stdout_xml=xml_output, stdout=json_output)
    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
