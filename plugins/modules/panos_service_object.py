#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_service_object
short_description: Create service objects on PAN-OS devices.
description:
    - Create service objects on PAN-OS devices.
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
            - Name of service object.
        type: str
        required: true
    protocol:
        description:
            - Protocol of the service.
        type: str
        choices: ['tcp', 'udp']
        default: 'tcp'
    source_port:
        description:
            - Source port of the service object.
        type: str
    destination_port:
        description:
            - Destination port of the service object.  Required if state is I(present).
        type: str
    description:
        description:
            - Descriptive name for this service object.
        type: str
    tag:
        description:
            - List of tags for this service object.
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create service object 'ssh-tcp-22'
  panos_service_object:
    name: 'ssh-tcp-22'
    destination_port: '22'
    description: 'SSH on tcp/22'
    tag: ['Prod']

- name: Create service object 'mysql-tcp-3306'
  panos_service_object:
    name: 'mysql-tcp-3306'
    destination_port: '3306'
    description: 'MySQL on tcp/3306'

- name: Delete service object 'mysql-tcp-3306'
  panos_service_object:
    name: 'mysql-tcp-3306'
    state: 'absent'
"""

RETURN = """
# Default return values
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    apply_state,
)


API_ENDPOINT = "/restapi/v10.0/Objects/Services"


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            protocol=dict(default="tcp", choices=["tcp", "udp"]),
            source_port=dict(type="str"),
            destination_port=dict(type="str"),
            description=dict(type="str"),
            tag=dict(type="list", elements="str"),
            state=dict(type="str", default="present", choices=["present", "absent"]),
        ),
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "description": module.params["description"],
            "protocol": {
                module.params["protocol"]: {
                    "port": module.params["destination_port"],
                    "source-port": module.params["source_port"],
                }
            },
            "tag": module.params["tag"],
        }
    }

    try:
        apply_state(module, spec, api_endpoint=API_ENDPOINT)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
