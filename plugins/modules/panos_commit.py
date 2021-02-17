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
module: panos_commit
short_description: Commit changes to a PAN-OS device.
description:
    - Commits changes to a PAN-OS device.
author:
    - Michael Richardson (@mrichardson03)
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is supported.
options:
    force:
        description:
            - Perform a force commit.
        type: bool
        default: False
    exclude_device_and_network:
        description:
            - Perform a partial commit, excluding device and network
              configurationa.
        type: bool
        default: False
    exclude_policy_and_objects:
        description:
            - Perform a partial commit, excluding policy and object
              configuration.
        type: bool
        default: False
    exclude_shared_objects:
        description:
            - Perform a partial commit, excluding shared object configuration.
        type: bool
        default: False
    description:
        description:
            - Description to add to commit.
        type: str
    admins:
        description:
            - Commit only the changes made by the specified administrators.
        type: list
        elements: str
    sleep:
        description:
            - Check commit status every X seconds.
        type: int
        default: 10
    timeout:
        description:
            - Generate an error if commit has not completed after X seconds.
        type: int
        default: 600
"""

EXAMPLES = """
- name: Commit firewall config
  panos_commit:

- name: commit changes by specified admins to firewall
  panos_commit:
    admins: ['admin1','admin2']
"""

RETURN = """
changed:
    description: A boolean value indicating if the task had to make changes.
    returned: always
    type: bool
msg:
    description: A string with an error message, if any.
    returned: failure, always
    type: str
stdout:
    description: output of the commit job as a JSON formatted string
    returned: always
    type: str
    sample: "{system: {app-release-date: 2017/05/01  15:09:12}}"
stdout_xml:
    description: output of the commit job as an XML formatted string
    returned: always
    type: str
    sample: "<response status=success><result><system><hostname>fw2</hostname>"
"""
