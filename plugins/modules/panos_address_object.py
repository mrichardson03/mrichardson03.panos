#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_address_object
short_description: Create address objects on PAN-OS devices.
description:
    - Create address objects on PAN-OS devices.
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
            - Name of object to create.
        required: true
        type: str
    value:
        description:
            - IP address, IP range, or FQDN for the object.  Must specify if state is I(present).
        type: str
    address_type:
        description:
            - Type of address object.
        choices: ['ip-netmask', 'ip-range', 'fqdn']
        type: str
        default: 'ip-netmask'
    description:
        description:
            - Descriptive name for this address object.
        type: str
    tag:
        description:
            - List of tags to add to this address object.
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create object 'Test-One'
  panos_address_object:
    name: 'Test-One'
    value: '1.1.1.1'
    description: 'Description One'
    tag: ['Prod']

- name: Create object 'Test-Two'
  panos_address_object:
    name: 'Test-Two'
    address_type: 'ip-range'
    value: '1.1.1.1-2.2.2.2'
    description: 'Description Two'
    tag: ['SI']

- name: Create object 'Test-Three'
  panos_address_object:
    name: 'Test-Three'
    address_type: 'fqdn'
    value: 'foo.bar.baz'
    description: 'Description Three'

- name: Delete object 'Test-Two'
  panos_address_object:
    name: 'Test-Two'
    state: 'absent'
"""

RETURN = """
# Default return values
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    apply_state,
)


API_ENDPOINT = "/restapi/v10.0/Objects/Addresses"


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            value=dict(),
            address_type=dict(
                default="ip-netmask", choices=["ip-netmask", "ip-range", "fqdn"]
            ),
            description=dict(),
            tag=dict(type="list", elements="str"),
            state=dict(type="str", default="present", choices=["present", "absent"]),
        ),
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            module.params["address_type"]: module.params["value"],
            "description": module.params["description"],
            "tag": module.params["tag"],
        }
    }

    try:
        apply_state(module, spec, api_endpoint=API_ENDPOINT)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
