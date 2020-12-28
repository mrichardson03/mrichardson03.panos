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
            - The type of dynamic update to request
        type: str
        default: content
        required: false
"""

EXAMPLES = """
- name: Install Latest Dynamic Content Updates
  panos_dynamic_updates:

- name: Install Latest Dynamic anti-virus Updates
  panos_dynamic_updates:
    content_type: anti-virus
"""

RETURN = """
changed:
    description: A boolean value indicating if the task had to make changes.
    returned: always
    type: bool
"""
