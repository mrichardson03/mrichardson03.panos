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
module: panos_facts
short_description: Collects facts from PAN-OS devices
description:
    - Collects fact information from Palo Alto Networks firewalls and Panorama.
author:
    - Michael Richardson (@mrichardson03)
notes:
    - Checkmode is not supported.
version_added: '1.0.0'
options:
    gather_subset:
        description:
            - Scopes what information is gathered from the device.
              Possible values for this argument include all, system, session,
              interfaces, ha, routing, vr, vsys and config. You can specify a
              list of values to include a larger subset. Values can also be used
              with an initial ! to specify that a specific subset should not be
              collected.  Panorama only supports the system, ha, and config
              subsets.
        required: false
        type: list
        elements: str
        default: ['!config']
"""

EXAMPLES = """
- name: Gather facts
  panos_facts:
    gather_subset: ['config']
"""

RETURN = """
ansible_net_version:
    description: PanOS version of the local node.
    returned: When C(system) is specified in C(gather_subset).
    type: str
"""

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            gather_subset=dict(default=["!config"], type="list", elements="str")
        ),
        supports_check_mode=False,
    )

    ansible_facts = dict()

    try:
        version_dict = module.connection.version()

        # Only return PAN-OS version for now.
        ansible_facts["ansible_net_version"] = version_dict["sw-version"]

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))

    module.exit_json(ansible_facts=ansible_facts)


if __name__ == "__main__":
    main()
