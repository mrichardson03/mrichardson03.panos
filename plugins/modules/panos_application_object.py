#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_application_object
short_description: Create application objects on PAN_OS devices.
description:
    - Create application objects on PAN_OS devices.
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
            - Name of the application.
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
            - Risk (1 - 5) of the application
        type: str
        choices: ['1', '2', '3', '4', '5']
    parent_app:
        description:
            - Parent Application for which this app falls under
        type: str
    timeout:
        description:
            - Default timeout
        type: int
    tcp_timeout:
        description:
            - TCP timeout
        type: int
    udp_timeout:
        description:
            - UDP timeout
        type: int
    tcp_half_closed_timeout:
        description:
            - TCP half closed timeout
        type: int
    tcp_time_wait_timeout:
        description:
            - TCP wait time timeout
        type: int
    evasive_behavior:
        description:
            - Application is actively evasive
        type: bool
    consume_big_bandwidth:
        description:
            - Application uses large bandwidth
        type: bool
    used_by_malware:
        description:
            - Application is used by malware
        type: bool
    able_to_transfer_file:
        description:
            - Application can do file transfers
        type: bool
    has_known_vulnerability:
        description:
            - Application has known vulnerabilities
        type: bool
    tunnel_other_application:
        description:
            - Application can tunnel other applications
        type: bool
    prone_to_misuse:
        description:
            - Application is prone to misuse
        type: bool
    pervasive_use:
        description:
            - Application is used pervasively
        type: bool
    file_type_ident:
        description:
            - Scan for files
        type: bool
    virus_ident:
        description:
            - Scan for viruses
        type: bool
    data_ident:
        description:
            - Scan for data types
        type: bool
    description:
        description:
            - Description of this object
        type: str
    tag:
        description:
            - Administrative tags
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create custom application
  panos_application_object:
    provider: '{{ provider }}'
    name: 'custom_app'
    category: 'business_systems'
    subcategory: 'auth_service'
    technology: 'client_server'
    risk: '1'

- name: Remove custom application
  panos_application_object:
    provider: '{{ provider }}'
    name: 'custom_app'
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
            category=dict(type="str"),
            subcategory=dict(type="str"),
            technology=dict(type="str"),
            description=dict(type="str"),
            timeout=dict(type="int"),
            tcp_timeout=dict(type="int"),
            udp_timeout=dict(type="int"),
            tcp_half_closed_timeout=dict(type="int"),
            tcp_time_wait_timeout=dict(type="int"),
            risk=dict(choices=["1", "2", "3", "4", "5"]),
            evasive_behavior=dict(type="bool"),
            consume_big_bandwidth=dict(type="bool"),
            used_by_malware=dict(type="bool"),
            able_to_transfer_file=dict(type="bool"),
            has_known_vulnerability=dict(type="bool"),
            tunnel_other_application=dict(type="bool"),
            # This element exists in the XML schema, but doesn't appear to be
            # set anywhere.
            # tunnel_applications=dict(type="bool"),
            prone_to_misuse=dict(type="bool"),
            pervasive_use=dict(type="bool"),
            file_type_ident=dict(type="bool"),
            virus_ident=dict(type="bool"),
            data_ident=dict(type="bool"),
            parent_app=dict(type="str"),
            tag=dict(type="list", elements="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/Applications",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "subcategory": module.params["subcategory"],
            "category": module.params["category"],
            "technology": module.params["technology"],
            "risk": module.params["risk"],
            "description": module.params["description"],
            "tag": module.params["tag"],
        }
    }

    for arg in [
        "evasive_behavior",
        "consume_big_bandwidth",
        "used_by_malware",
        "able_to_transfer_file",
        "has_known_vulnerability",
        "tunnel_other_application",
        "prone_to_misuse",
        "pervasive_use",
        "file_type_ident",
        "virus_ident",
        "data_ident",
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
