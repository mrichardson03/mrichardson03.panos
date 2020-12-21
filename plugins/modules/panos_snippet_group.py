#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Copyright 2020 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
