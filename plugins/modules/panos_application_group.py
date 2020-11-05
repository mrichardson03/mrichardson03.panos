#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_application_group
short_description: Create application groups on PAN-OS devices.
description:
    - Create application groups on PAN-OS devices.
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
    value:
        description:
            - List of applications to add to the group
        type: list
        elements: str
    tag:
        description:
            - Administrative tags
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create application group
  panos_application_group:
    name: 'Software Updates'
    value:
        - ms-update
        - apple-update
        - adobe-update
        - google-update
        - ms-product-activation
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
            value=dict(type="list", elements="str"),
            tag=dict(type="list", elements="str"),
        ),
        required_if=[["state", "present", ["value"]]],
        api_endpoint="/restapi/v10.0/Objects/ApplicationGroups",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "members": {"member": module.params["value"]},
            "tag": module.params["tag"],
        }
    }

    try:
        module.apply_state(spec)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
