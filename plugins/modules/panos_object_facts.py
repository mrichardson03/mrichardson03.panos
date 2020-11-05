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
    - 'Michael Richardson (@mrichardson03)'
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
            - application-filter
            - application-group
            - custom-url-category
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

from ansible.module_utils.connection import ConnectionError

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)

OBJ_TYPES = {
    "address": "Addresses",
    "address-group": "AddressGroups",
    "application": "ApplicationObjects",
    "application-filter": "ApplicationFilters",
    "application-group": "ApplicationGroups",
    "custom-url-category": "CustomURLCategories",
    "service": "Services",
    "service-group": "ServiceGroups",
    "tag": "Tags",
}


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(),
            object_type=dict(default="address", choices=OBJ_TYPES.keys()),
        )
    )

    name = module.params["name"]
    object_type = module.params["object_type"]

    module.api_endpoint = "/restapi/v10.0/Objects/{0}".format(OBJ_TYPES[object_type])

    try:
        objects = module.fetch_objects(name=name)

        module.exit_json(changed=False, ansible_module_results=objects, objects=objects)
    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
