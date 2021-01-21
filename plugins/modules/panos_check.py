#!/usr/bin/python

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
options:
  delay:
    description:
      - Number of seconds to wait before starting checks.
    default: 0
    type: int
  sleep:
    description:
      - Number of seconds to wait in between checks.
    default: 60
    type: int
  timeout:
    description:
      - Maximum number of seconds to poll the PAN-OS device.
    default: 600
    type: int
"""

EXAMPLES = """
- name: Check if the device is ready
  panos_check:
"""

RETURN = """
elapsed:
  description: Number of seconds until the device was ready.
  returned: success
  type: int
msg:
  description: Status message on success or failure.
  returned: always
  type: str
"""
