#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_object_facts
short_description: Retreives facts about objects on PAN-OS devices.
description:
    - Retrieves facts about objects on PAN-OS devices.
author:
    - Michael Richardson (@mrichardson03)
notes:
    - Check mode is not supported.
version_added: '1.0.0'
options:
    name:
        description:
            - Name of object to retrieve.
        type: str
    object_type:
        description:
            - Type of object to retrieve.
        type: str
        choices:
            - address
            - address-group
            - application
            - application-group
            - service
            - service-group
            - tag
        default: address
"""

EXAMPLES = """
- name: Retrieve address group object 'Prod'
  panos_object_facts:
    name: 'Prod'
    object_type: 'address-group'
  register: result

- name: Retrieve service group object 'Prod-Services'
  panos_object_facts:
    provider: '{{ provider }}'
    name: 'Prod-Services'
    object_type: 'service-group'
  register: result
"""

RETURN = """

"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    fetch_objects,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(),
            object_type=dict(
                default="address",
                choices=[
                    "address",
                    "address-group",
                    "application",
                    "application-group",
                    "service",
                    "service-group",
                    "tag",
                ],
            ),
        )
    )

    obj_types = {
        "address": "Addresses",
        "address-group": "AddressGroups",
        "application": "Applications",
        "application-group": "ApplicationGroups",
        "service": "Services",
        "service-group": "ServiceGroups",
        "tag": "Tags",
    }

    try:
        conn = Connection(module._socket_path)

        object_type = module.params["object_type"]
        api_endpoint = "/restapi/v10.0/Objects/{0}".format(obj_types[object_type])

        objects = fetch_objects(conn, api_endpoint)

        module.exit_json(changed=False, objects=objects["result"])
    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
