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
short_description: Execute an operational command on PAN-OS devices.
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
            - Execute this string directly as an operational command.
        type: str
        required: true
    cmd_is_xml:
        description:
            - If true, treat the cmd option as a string already in XML format.
            - If false, attempt to convert it to XML before execution.
        type: bool
        default: false
"""

EXAMPLES = """
- name: show system info
  panos_op:
    cmd: 'show system info'

- name: show system info (as XML)
  panos_op:
    cmd: '<show><system><info/></system></show>'
    cmd_is_xml: true
"""

RETURN = """
stdout:
    description: Output of the command in native XML format.
    returned: always
    type: str
    sample: "<response status=success><result><system><hostname>fw2</hostname>"

stdout_dict:
    description: Output of 'cmd', but converted into a dictionary format.
    returned: When 'cmd' is specified.
    type: dict
    sample: >
        {
            'response': {
                '@status': 'success',
                'result': {
                    'system': {
                        'hostname': 'fw2',
                        ...
                    }
                }
            }
        }
"""

try:
    import xmltodict

    HAS_LIB = True
except ImportError:  # pragma: no cover
    HAS_LIB = False

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
    get_nested_key,
)


def execute_op_cmd(conn, cmd, cmd_is_xml):
    """Executes an operational command."""
    changed = True

    safe_cmds = ["diff", "show"]
    safe_xml_cmds = ["<diff>", "<show>"]

    if cmd_is_xml:
        for safe_xml_cmd in safe_xml_cmds:
            if cmd.find(safe_xml_cmd) == 0:
                changed = False

    else:
        for safe_cmd in safe_cmds:
            if cmd.find(safe_cmd) == 0:
                changed = False

    xml_output = conn.op(cmd, is_xml=cmd_is_xml)
    obj_dict = xmltodict.parse(xml_output)

    return {"changed": changed, "stdout": xml_output, "stdout_dict": obj_dict}


def show_job_id(conn, job_id):
    """Retrieves job results for a given job id."""
    results = execute_op_cmd(conn, f"<show><jobs><id>{job_id}</id></jobs></show>", True)
    job_results = get_nested_key(results, ["stdout_dict", "response", "result", "job"])

    results["job"] = {}

    for k, v in job_results.items():
        if v is not None:
            results["job"][k] = v

    del results["stdout_dict"]
    return results


def check_job_type(conn, job_type):
    """Retrieves the most recent results for a given job type."""
    results = execute_op_cmd(conn, "show jobs all", False)
    jobs = get_nested_key(results, ["stdout_dict", "response", "result", "job"])

    results["job"] = None

    if jobs:
        if isinstance(jobs, dict):
            jobs = [jobs]

        for j in jobs:
            if j["type"] == job_type:
                results["job"] = {}

                for k, v in j.items():
                    if v is not None:
                        results["job"][k] = v

    if results["job"] is None:
        raise ConnectionError("Requested job not found.")

    del results["stdout_dict"]
    return results


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            cmd=dict(type="str", required=True),
            cmd_is_xml=dict(default=False, type="bool"),
        ),
        supports_check_mode=False,
    )

    if not HAS_LIB:  # pragma: no cover
        module.fail_json(msg="Missing required libraries.")

    cmd = module.params["cmd"]
    cmd_is_xml = module.params["cmd_is_xml"]

    results = None

    try:
        results = execute_op_cmd(module.connection, cmd, cmd_is_xml)
        module.exit_json(**results)
    except ConnectionError as e:  # pragma: no cover
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":  # pragma: no cover
    main()
