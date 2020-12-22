#!/usr/bin/python

# Copyright 2020 Palo Alto Networks, Inc
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_service_group
short_description: Create service group objects on PAN-OS devices.
description:
    - Create service group objects on PAN-OS devices.
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
            - Name of service group.
        type: str
        required: true
    value:
        description:
            - List of service objects to be included in the group.  Must
              specify if state is present.
        type: list
        elements: str
    tag:
        description:
            - List of tags for this service group.
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create service group 'Prod-Services'
  panos_service_group:
    name: 'Prod-Services'
    value: ['ssh-tcp-22', 'mysql-tcp-3306']

- name: Delete service group 'Prod-Services'
  panos_service_group:
    name: 'Prod-Services'
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
            value=dict(type="list", elements="str"),
            tag=dict(type="list", elements="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/ServiceGroups",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "members": {"member": module.params["value"]},
            "tag": module.params["tag"],
        }
    }

    if module.params["state"] == "present" and module.params["value"] is None:
        module.fail_json(msg="Must specify 'value' if 'state' is 'present'.")

    try:
        changed, diff = module.apply_state(spec)

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
