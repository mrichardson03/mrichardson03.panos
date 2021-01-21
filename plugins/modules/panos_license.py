#!/usr/bin/python

#  Copyright 2020 Palo Alto Networks, Inc
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
module: panos_license
short_description: Apply a license authcode to a PAN-OS device
description:
    - Apply a license authcode to a PAN-OS device.
    - The authcode should have been previously registered on the Palo Alto Networks support portal.
    - The device should have Internet access.
author: Michael Richardson (@mrichardson03)
version_added: '1.0.0'
notes:
    - Panorama is supported
    - Check mode is supported.
options:
    authcode:
        description:
            - Authcode to be applied.
        type: str
"""

EXAMPLES = """
- name: License the the device
  panos_license:
    authcode: "IBADCODE"
  register: result

- debug:
    msg: 'Serial number is {{ result.serial }}'
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
serial:
    description: Serial number after authcode application.  Licensing VM-Series will generate a serial number.
    returned: success
    type: str
    sample: 007200004214
licenses:
    description: Licenses after authcode application.
    returned: success
    type: list
    elements: dict
"""

# import time
# import xml.etree.ElementTree

# from ansible.module_utils.connection import ConnectionError
# from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
#     PanOSAnsibleModule,
# )

# try:
#     import xmltodict

#     HAS_LIB = True
# except ImportError:
#     HAS_LIB = False


# def execute_op(module, cmd):
#     op_xml = module.connection.op(cmd=cmd, is_xml=True)
#     return xml.etree.ElementTree.fromstring(op_xml)


# def get_licenses(module):
#     response = module.connection.op(cmd="request license info")
#     parsed = xmltodict.parse(response, force_list=("entry"))
#     licenses = parsed.get("response").get("result").get("licenses", None)

#     if licenses is None:
#         return []
#     else:
#         parsed.get("response").get("result").get("licenses").get("entry", [])


# def main():
#     module = PanOSAnsibleModule(
#         argument_spec=dict(
#             authcode=dict(
#                 required=False,
#                 type="str",
#             )
#         ),
#         supports_check_mode=True,
#     )

#     if not HAS_LIB:
#         module.exit_json(msg="Missing required libraries.")

#     changed = False
#     licenses = []
#     serial = None

#     try:
#         device_info = module.connection.version()

#         if module.params["authcode"]:
#             licenses = get_licenses(module)

#             if licenses == []:
#                 if not module.check_mode:
#                     module.connection.op(
#                         cmd="<request><license><fetch><auth-code>{0}</auth-code></fetch></license></request>".format(
#                             module.params["authcode"]
#                         ),
#                         is_xml=True,
#                         validate=False,
#                     )

#                     module.connection.close()

#                 changed = True

#                 if device_info.get("model") == "PA-VM":
#                     time.sleep(300)  # completely unscientific amount of time
#                     device_info = module.connection.version(refresh=True)

#         serial = device_info.get("serial", None)
#         licenses = get_licenses(module)

#     except ConnectionError as e:
#         module.fail_json(msg="{0}".format(e))

#     module.exit_json(changed=changed, serial=serial, licenses=licenses)


# if __name__ == "__main__":
#     main()
