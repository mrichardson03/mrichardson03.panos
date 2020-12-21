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
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
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
