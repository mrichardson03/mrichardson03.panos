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
module: panos_software
short_description: Install a PAN-OS software release.
description:
    - Install a PAN-OS software release.
author:
    - 'Michael Richardson (@mrichardson03)'
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is supported.
options:
    version:
        description:
            - Desired PAN-OS release for target device.  If this version is in
              the next PAN-OS release, the base image for that release will be
              downloaded as well.
            - For example, if the PAN-OS device is currently running 9.1.0, and
              'version' is set to 10.0.2, the 10.0.0 base image will be
              downloaded and the 10.0.2 image will be downloaded and installed.
        type: str
        required: true
    sync_to_peer:
        description:
            - If device is a member of a HA pair, perform actions on the peer
              device as well.  Only used when downloading software,
              installation must be performed on both devices.
        type: bool
        default: False
    download:
        description:
            - Download PAN-OS version to the device.
        type: bool
        default: True
    install:
        description:
            - Perform installation of the PAN-OS version on the device.
        type: bool
        default: True
    restart:
        description:
            - Restart device after installing desired version.  Use in conjunction with
              panos_check to determine when firewall is ready again.
        type: bool
        default: False
    timeout:
        description:
            - Maximum amount of time (in seconds) each software download or
              installation job performed by this module is allowed to run before
              error.
        type: int
        default: 600
"""

EXAMPLES = """
- name: Install PAN-OS 8.1.6 and restart
  panos_software:
    version: '8.1.6'
    restart: true

- name: Download PAN-OS 9.0.0 base image only
  panos_software:
    version: '9.0.0'
    install: false
    restart: false

- name: Download PAN-OS 9.0.1 and sync to HA peer
  panos_software:
    version: '9.0.1'
    sync_to_peer: true
    install: false
    restart: false
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
"""
