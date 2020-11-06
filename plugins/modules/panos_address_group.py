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
module: panos_address_group
short_description: Create address group objects on PAN-OS devices.
description:
    - Create address group objects on PAN-OS devices.
author:
    - Michael Richardson (@mrichardson03)
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is supported.
extends_documentation_fragment:
    - mrichardson03.panos.fragments.state
options:
    name:
        description:
            - Name of address group to create.
        required: true
        type: str
    static_value:
        description:
            - List of address objects to be included in the group.
        type: list
        elements: str
    dynamic_value:
        description:
            - Registered IP tags for a dynamic address group.
        type: str
    description:
        description:
            - Descriptive name for this address group.
        type: str
    tag:
        description:
            - List of tags to add to this address group.
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create object group 'Prod'
  panos_address_group:
    name: 'Prod'
    static_value: ['Test-One', 'Test-Three']
    tag: ['Prod']

- name: Create object group 'SI'
  panos_address_group:
    name: 'SI'
    dynamic_value: "'SI_Instances'"
    tag: ['SI']

- name: Delete object group 'SI'
  panos_address_group:
    name: 'SI'
    state: 'absent'
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
diff:
    description:
        - Information about the differences between the previous and current
          state.
        - Contains 'before' and 'after' keys.
    returned: success, when needed
    type: dict
    elements: str
"""

from ansible.module_utils.connection import ConnectionError

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            static_value=dict(type="list", elements="str"),
            dynamic_value=dict(),
            description=dict(),
            tag=dict(type="list", elements="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/AddressGroups",
        with_state=True,
        mutually_exclusive=[["static_value", "dynamic_value"]],
        supports_check_mode=True,
    )

    if module.params["state"] == "present":
        if (
            module.params["static_value"] is None
            and module.params["dynamic_value"] is None
        ):
            module.fail_json(
                msg="One of 'static_value' or 'dynamic_value' is required when "
                "state' is 'present'"
            )

    # Object params.
    spec = {
        "entry": {
            "@name": module.params["name"],
            "description": module.params["description"],
            "tag": module.params["tag"],
        }
    }

    if module.params["static_value"]:
        spec["entry"]["static"] = {"member": module.params["static_value"]}
    else:
        spec["entry"]["dynamic"] = {"filter": module.params["dynamic_value"]}

    try:
        changed, diff = module.apply_state(spec)

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
