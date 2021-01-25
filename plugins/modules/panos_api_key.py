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
module: panos_api_key
short_description: Generate an API key for a specified user
description:
    - Generate an API key for a specified user
author:
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

from ansible.module_utils.connection import ConnectionError
from ansible_collections.paloaltonetworks.panos_enhanced.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(argument_spec={}, supports_check_mode=False)

    try:
        api_key = module.connection.api_key()

        if api_key is not None:
            module.exit_json(changed=False, api_key=api_key)
        else:
            module.fail_json(msg="Invalid credential")
    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
