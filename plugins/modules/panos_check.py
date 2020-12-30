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
module: panos_check
short_description: Checks to see if a PAN-OS device is ready for configuration.
description:
    - Checks to see if the autocommit job on a PAN-OS device has completed,
      marking the device ready for configuration.
author:
    - Michael Richardson (@mrichardson03)
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is NOT supported.
    - This module can take a long amount of time to execute.  It is recommended
      to adjust the Ansible persistent connection timeout to a larger value than
      the default of 30 seconds.  See the
      U(Command Timeout,https://docs.ansible.com/ansible/latest/network/user_guide/network_debug_troubleshooting.html#command-timeout)
      section in the Ansible Network Debug and Troubleshooting Guide for more
      information.
"""

EXAMPLES = """
- name: Check if the device is ready
  panos_check:
  register: result
  until: result is not failed
  retries: 30
  delay: 60
"""

RETURN = """
msg:
    description: A string specifying if the device is ready for configuration.
    returned: always
    type: str
"""

import xml.etree.ElementTree

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def check_autocommit(jobs):
    if len(jobs) == 0:
        return False

    for j in jobs:
        job_type = j.findtext(".//type")
        job_result = j.findtext(".//result")

        if job_type == "AutoCom" and job_result == "OK":
            return True
        else:
            return False

    # If we get to this point, the autocommit job is no longer in the job
    # history and it is assumed the device is ready.
    return True


def main():
    module = PanOSAnsibleModule(argument_spec={}, supports_check_mode=False)

    try:
        result = module.connection.op("show jobs all")
        jobs = xml.etree.ElementTree.fromstring(result).findall(".//job")

        if check_autocommit(jobs):
            module.exit_json(msg="Device ready.")
        else:
            module.fail_json(msg="Device not ready.")
    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
