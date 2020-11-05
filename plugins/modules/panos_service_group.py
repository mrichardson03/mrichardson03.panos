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
module: panos_service_group
short_description: Create service group objects on PAN-OS devices.
description:
    - Create service group objects on PAN-OS devices.
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
            - Name of service group.
        type: str
        required: true
    value:
        description:
            - List of service objects to be included in the group.  Must
              specify if state is present.
        type: list
        elements: str
    tag:
        description:
            - List of tags for this service group.
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create service group 'Prod-Services'
  panos_service_group:
    provider: '{{ provider }}'
    name: 'Prod-Services'
    value: ['ssh-tcp-22', 'mysql-tcp-3306']

- name: Delete service group 'Prod-Services'
  panos_service_group:
    provider: '{{ provider }}'
    name: 'Prod-Services'
    state: 'absent'
"""

RETURN = """
# Default return values
"""

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            value=dict(type="list", elements="str"),
            tag=dict(type="list", elements="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/ServiceGroups",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "members": {"member": module.params["value"]},
            "tag": module.params["tag"],
        }
    }

    if module.params["state"] == "present" and module.params["value"] is None:
        module.fail_json(msg="Must specify 'value' if 'state' is 'present'.")

    try:
        module.apply_state(spec)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
