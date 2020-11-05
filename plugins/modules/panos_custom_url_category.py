#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Copyright 2018 Palo Alto Networks, Inc
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
module: panos_custom_url_category
short_description: Create custom url category objects on PAN-OS devices.
description:
    - Create custom url category objects on PAN-OS devices.
author: "Michael Richardson (@mrichardson03)"
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is supported.
extends_documentation_fragment:
    - mrichardson03.panos.fragments.state
options:
    name:
        description:
            - Name of the tag.
        type: str
        required: true
    list:
        description:
            - List containing URLs or URL categories.
        type: list
        elements: str
        aliases:
            - url_value
    type:
        description:
            - Type of the custom category.
            - URL List will add the list of URLs to the custom category.
            - Category Match will match all of the specified URL categories.
        type: str
        choices: ['URL List', 'Category Match']
        default: 'URL List'
"""

EXAMPLES = """
- name: Create Custom Url Category 'Internet Access List'
  panos_custom_url_category:
    name: 'Internet Access List'
    url_value:
        - microsoft.com
        - redhat.com

- name: Remove Custom Url Category 'Internet Access List'
  panos_tag_object:
    name: 'Internet Access List'
    state: 'absent'
"""

RETURN = """
# Default return values
"""

from ansible.module_utils.connection import ConnectionError

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            list=dict(type="list", elements="str", aliases=["url_value"]),
            type=dict(
                type="str", choices=["URL List", "Category Match"], default="URL List"
            ),
        ),
        api_endpoint="/restapi/v10.0/Objects/ApplicationFilters",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "list": {"member": module.params["list"]},
            "type": module.params["type"],
        }
    }

    try:
        module.apply_state(spec)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
