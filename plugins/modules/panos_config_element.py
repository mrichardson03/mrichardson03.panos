#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_config_element
short_description: Sets arbitrary configuration element in the PAN-OS configuration
description:
    - This module will allow user to pass an xpath and element to be 'set' in the PAN-OS configuration.
author:
    - 'Nathan Embery (@nembery)'
version_added: '1.0.0'
requirements: []

notes:
    - Checkmode is supported.
    - Panorama is supported.
options:
    xpath:
        description:
            - The xpath address where the XML snippet will be inserted into the PAN-OS configuration
        type: str
        required: true
    element:
        description:
            - The XML snippet to be inserted into the PAN-OS configuration
        type: str
        required: true
    override:
        description:
            - Override existing configuration elements if True, otherwise, merge with existing configuration elements
        type: bool
        required: false
"""

EXAMPLES = """
- name: configure login banner
  vars:
    banner_text: 'Authorized Personnel Only!'
  panos_config_element:
    xpath: '/config/devices/entry[@name="localhost.localdomain"]/deviceconfig/system'
    element: '<login-banner>{{ banner_text }}</login-banner>'

"""

RETURN = """
diff:
    description: Differences found from existing running configuration and requested element
    returned: success
    type: str
    sample: {"before": "", "after": ""}
"""

from ansible.module_utils.connection import ConnectionError

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            xpath=dict(required=True), element=dict(required=True),
            override=dict(type="bool", default=False, required=False)
        ),
        supports_check_mode=True,
    )

    xpath = module.params["xpath"]
    element = module.params["element"]

    override = module.params.get('override', False)

    try:
        existing = module.connection.get(xpath)

        changed = True

        if existing == element or module.check_mode:
            changed = False

        if changed:
            if override:
                module.connection.edit(xpath, element)
            else:
                module.connection.set(xpath, element)

        diff = {'before': existing, 'after': element}

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
