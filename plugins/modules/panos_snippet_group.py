#!/usr/bin/python

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
