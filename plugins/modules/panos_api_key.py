#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_api_key
short_description: Generate an API key for a specified user
description:
    - Generate an API key for a specified user
author:
    - Joshua Colson (@freakinhippie)
    - Garfield Lee Freeman (@shinmog)
    - Michael Richardson (@mrichardson03)
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is NOT supported.
"""

EXAMPLES = """
- name: Generate API key
  panos_api_key:
  register: api_key

- debug:
    msg: '{{ auth.api_key }}'
"""

RETURN = """
api_key:
    description: Generated API key
    returned: success
    type: str
    sample: "LUFRPT14MW5xOEo1R09KVlBZNnpnemh0VHRBOWl6TGM9bXcwM3JHUGVhRlNiY0dCR0srNERUQT09"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.connection import Connection
from ansible.module_utils.connection import ConnectionError


def main():
    module = AnsibleModule(argument_spec={}, supports_check_mode=False)

    try:
        conn = Connection(module._socket_path)
        api_key = conn.api_key()

        if api_key is not None:
            module.exit_json(changed=False, api_key=api_key)
        else:
            module.fail_json(msg="Invalid credential")
    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
