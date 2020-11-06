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
    tcp_override:
        description:
            - Specify custom TCP timeouts for this service.
        type: bool
        default: False
    tcp_override_timeout:
        description:
            - Set the maximum TCP session timeout (in seconds) for this service.
        type: str
        default: 3600
    tcp_override_halfclose_timeout:
        description:
            - Set the maximum length of time (in seconds) a TCP session can
              remain open when only one side of the connection has attempted to
              close the connection.
        type: str
        default: 120
    tcp_override_timewait_timeout:
        description:
            - Set the maximum length of time (in seconds) a TCP session can
              remain open after recieving the second of the two FIN packets
              required to terminate a session, or after receiving an RST packet
              to reset a connection.
        type: str
        default: 15
    udp_override:
        description:
            - Specify custom UDP timeouts for this service.
        type: bool
        default: False
    udp_override_timeout:
        description:
            - Set the maximum UDP session timeout (in seconds) for this service.
        type: str
        default: 30
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
            name=dict(required=True),
            protocol=dict(default="tcp", choices=["tcp", "udp"]),
            source_port=dict(type="str"),
            destination_port=dict(type="str"),
            description=dict(type="str"),
            tcp_override=dict(type="bool", default=False),
            tcp_override_timeout=dict(type="str", default="3600"),
            tcp_override_halfclose_timeout=dict(type="str", default="120"),
            tcp_override_timewait_timeout=dict(type="str", default="15"),
            udp_override=dict(type="bool", default=False),
            udp_override_timeout=dict(type="str", default="30"),
            tag=dict(type="list", elements="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/Services",
        with_state=True,
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

    tcp_override = {"override": {"no": {}}}

    if module.params["tcp_override"]:
        tcp_override = {"override": {"yes": {}}}

        if module.params["tcp_override_timeout"]:
            tcp_override["override"]["yes"].update(
                {"timeout": module.params["tcp_override_timeout"]}
            )

        if module.params["tcp_override_halfclose_timeout"]:
            tcp_override["override"]["yes"].update(
                {"halfclose-timeout": module.params["tcp_override_halfclose_timeout"]}
            )

        if module.params["tcp_override_timewait_timeout"]:
            tcp_override["override"]["yes"].update(
                {"timewait-timeout": module.params["tcp_override_timewait_timeout"]}
            )

    if module.params["protocol"] == "tcp":
        spec["entry"]["protocol"]["tcp"].update(tcp_override)

    udp_override = {"override": {"no": {}}}

    if module.params["udp_override"]:
        udp_override = {"override": {"yes": {}}}

        if module.params["udp_override_timeout"]:
            udp_override["override"]["yes"].update(
                {"timeout": module.params["udp_override_timeout"]}
            )

    if module.params["protocol"] == "udp":
        spec["entry"]["protocol"]["udp"].update(udp_override)

    try:
        changed, diff = module.apply_state(spec)

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
