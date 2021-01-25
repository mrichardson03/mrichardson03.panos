#!/usr/bin/python

# Copyright 2021 Palo Alto Networks, Inc
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

DOCUMENTATION = """
---
module: panos_address_object
short_description: Create address objects on PAN-OS devices.
description:
    - Create address objects on PAN-OS devices.
author:
    - Michael Richardson (@mrichardson03)
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is supported.
extends_documentation_fragment:
    - paloaltonetworks.panos_enhanced.fragments.state
options:
    name:
        description:
            - Name of object to create.
        required: true
        type: str
    value:
        description:
            - IP address, IP range, or FQDN for the object.  Must specify if state is I(present).
        type: str
    address_type:
        description:
            - Type of address object.
        choices: ['ip-netmask', 'ip-range', 'fqdn']
        type: str
        default: 'ip-netmask'
    description:
        description:
            - Descriptive name for this address object.
        type: str
    tag:
        description:
            - List of tags to add to this address object.
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create object 'Test-One'
  panos_address_object:
    name: 'Test-One'
    value: '1.1.1.1'
    description: 'Description One'
    tag: ['Prod']

- name: Create object 'Test-Two'
  panos_address_object:
    name: 'Test-Two'
    address_type: 'ip-range'
    value: '1.1.1.1-2.2.2.2'
    description: 'Description Two'
    tag: ['SI']

- name: Create object 'Test-Three'
  panos_address_object:
    name: 'Test-Three'
    address_type: 'fqdn'
    value: 'foo.bar.baz'
    description: 'Description Three'

- name: Delete object 'Test-Two'
  panos_address_object:
    name: 'Test-Two'
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
