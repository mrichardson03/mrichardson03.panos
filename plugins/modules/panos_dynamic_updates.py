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
short_description: Installs PAN-OS dynamic updates.
description:
    - Installs the latest version of one or more PAN-OS dynamic updates.
author:
    - 'Nathan Embery (@nembery)'
    - 'Michael Richardson (@mrichardson03)'
version_added: '1.0.0'
requirements: []
notes:
    - Check mode is supported.
    - Panorama is supported.
options:
    content_type:
        description:
            - The types of dynamic updates to install.
        type: list
        elements: str
        default: ['content']
        choices:
            - content
            - anti-virus
            - wildfire
"""

EXAMPLES = """
- name: Install content updates
  panos_dynamic_updates:

- name: Install latest WildFire update
  panos_dynamic_updates:
    content_type: ['wildfire']
"""

RETURN = """
changed:
    description: A boolean value indicating if the task made any changes.
    returned: always
    type: bool
content:
    description: Content version number, if installed.
    returned: if installed
    type: str
anti-virus:
    description: Anti-virus version number, if installed.
    returned: if installed
    type: str
wildfire:
    description: WildFire version number, if installed.
    returned: if installed
    type: str
"""
