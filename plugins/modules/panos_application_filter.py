#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_application_filter
short_description: Create application filters on PAN-OS devices.
description:
    - Create application filters on PAN-OS devices.
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
    category:
        description:
            - Application category
        type: str
    subcategory:
        description:
            - Application subcategory
        type: str
    technology:
        description:
            - Application technology
        type: str
    risk:
        description:
            - Risk (1-5) of the application
        type: str
        choices: ['1', '2', '3', '4', '5']
    evasive:
        description:
            - If the applications are evasive
        type: bool
    excessive_bandwidth_use:
        description:
            - If the applications use excessive bandwidth
        type: bool
    prone_to_misuse:
        description:
            - If the applications are prone to misuse
        type: bool
    is_saas:
        description:
            - If the applications are SaaS
        type: bool
    transfers_files:
        description:
            - If the applications transfer files
        type: bool
    tunnels_other_apps:
        description:
            - If the applications tunnel other applications
        type: bool
    used_by_malware:
        description:
            - If the applications are used by malware
        type: bool
    has_known_vulnerabilities:
        description:
            - If the applications have known vulnerabilities
        type: bool
    pervasive:
        description:
            - If the applications are used pervasively
        type: bool
    tag:
        description:
            - Administrative tags
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create application filter
  panos_application_filter:
    name: 'custom-apps'
    category: 'business-systems'
    subcategory: 'auth-service'
    technology: 'client-server'
    risk: '1'

- name: Remove custom application
  panos_application_filter:
    name: 'custom-apps'
    state: 'absent'
"""

RETURN = """
# Default return values
"""

from ansible.module_utils.connection import ConnectionError

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
    booltostr,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            category=dict(type="list", element="str"),
            subcategory=dict(type="list", element="str"),
            technology=dict(type="list", element="str"),
            risk=dict(type="list", elements="str", choices=["1", "2", "3", "4", "5"]),
            evasive=dict(type="bool"),
            excessive_bandwidth_use=dict(type="bool"),
            used_by_malware=dict(type="bool"),
            transfers_files=dict(type="bool"),
            has_known_vulnerabilities=dict(type="bool"),
            tunnels_other_apps=dict(type="bool"),
            prone_to_misuse=dict(type="bool"),
            pervasive=dict(type="bool"),
            is_saas=dict(type="bool"),
            tag=dict(type="list", elements="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/ApplicationFilters",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "category": {"member": module.params["category"]},
            "subcategory": {"member": module.params["subcategory"]},
            "technology": {"member": module.params["technology"]},
            "risk": {"member": module.params["risk"]},
            "tag": module.params["tag"],
        }
    }

    for arg in [
        "evasive",
        "excessive_bandwidth_use",
        "used_by_malware",
        "transfers_files",
        "prone_to_misuse",
        "pervasive",
        "is_saas",
        "transfers_files",
        "tunnels_other_apps",
        "has_known_vulnerabilities",
    ]:
        spec_key = arg.replace("_", "-")

        if module.params[arg]:
            spec["entry"][spec_key] = booltostr(module.params[arg])

    try:
        module.apply_state(spec)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
