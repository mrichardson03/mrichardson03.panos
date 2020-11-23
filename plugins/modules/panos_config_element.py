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
version_added: '1.0.1'
requirements: []

notes:
    - Checkmode is NOT supported.
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
"""

EXAMPLES = """
- name: configure some xpath and element
  panos_config_element:
    xpath: '/some/xpath'
    element: '<xml>hi there</xml>'

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
            xpath=dict(required=True), element=dict(required=True)
        ),
        supports_check_mode=False,
    )

    xpath = module.params["xpath"]
    element = module.params["element"]

    try:
        changed, diff = module.set_at_xpath(xpath, element)

        module.exit_json(changed=changed, diff=diff)
    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
