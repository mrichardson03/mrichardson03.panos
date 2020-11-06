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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: panos_region
short_description: Create regions on PAN-OS devices.
description:
    - Create regions on PAN-OS devices.
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
            - Name of the object.
        type: str
        required: true
    address:
        description:
            - List of IP networks
        type: list
        elements: str
    latitude:
        description:
            - Latitude of the region
        type: str
    longitude:
        description:
            - Longitude of the region
        type: str
"""

EXAMPLES = """
- name: Create region
  panos_region:
    name: 'Palo-Alto-Networks'
    address:
        - '192.168.0.0/16'
    latitude: 37.383415
    longitude: -121.982882
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

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            address=dict(type="list", elements="str"),
            latitude=dict(type="str"),
            longitude=dict(type="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/Regions",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "geo-location": {
                "latitude": module.params["latitude"],
                "longitude": module.params["longitude"],
            },
            "address": {"member": module.params["address"]},
        }
    }

    try:
        changed, diff = module.apply_state(spec)

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
