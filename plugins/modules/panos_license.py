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
module: panos_license
short_description: Apply a license authcode to a PAN-OS device
description:
    - Apply a license authcode to a PAN-OS device.
    - The authcode should have been previously registered on the Palo Alto Networks support portal.
    - The device should have Internet access.
author: Michael Richardson (@mrichardson03)
version_added: '1.0.0'
notes:
    - Panorama is supported
    - Check mode is supported.
options:
    authcode:
        description:
            - Authcode to be applied.
        type: str
"""

EXAMPLES = """
- name: License the the device
  panos_license:
    authcode: "IBADCODE"
  register: result

- debug:
    msg: 'Serial number is {{ result.serial }}'
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
serial:
    description: Serial number after authcode application.  Licensing VM-Series will generate a serial number.
    returned: success
    type: str
    sample: 007200004214
licenses:
    description: Licenses after authcode application.
    returned: success
    type: list
    elements: dict
"""
