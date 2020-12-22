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
module: panos_snippet_group
short_description: Sets arbitrary configuration elements from a snippet group definition file
description:
    - This module will allow user the creation and use of custom configuration definitions using a YAML file
author:
    - 'Nathan Embery (@nembery)'
version_added: '1.0.0'
requirements: []

notes:
    - Checkmode is supported.
    - Panorama is supported.
options:
    src:
        description:
            - The relative path to a snippet definition file to load
        type: str
        required: true
"""

EXAMPLES = """
- name: Custom BGP Configuration
  vars:
    asn: 64512
    peer_asn: 64515
  panos_snippet_group:
    src: bgp.yaml

"""

RETURN = """
snippets:
    description: List of differences found from existing running configuration and requested snippets
    returned: success
    type: str
    sample: {"FIXME": "", "after": ""}
"""
