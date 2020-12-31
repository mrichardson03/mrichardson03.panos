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

import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection, ConnectionError

PANOS_API_CODES = {
    "400": "Bad Request",
    "403": "Forbidden",
    "1": "Unknown Command",
    "2": "Internal Error",
    "3": "Internal Error",
    "4": "Internal Error",
    "5": "Internal Error",
    "6": "Bad Xpath",
    "7": "Object not present",
    "8": "Object not unique",
    "10": "Reference count not zero",
    "11": "Internal Error",
    "12": "Invalid Object",
    "14": "Operation Not Possible",
    "15": "Operation Denied",
    "16": "Unauthorized",
    "17": "Invalid Command",
    "18": "Malformed Command",
    "19": "Success",
    "20": "Success",
    "21": "Internal Error",
    "22": "Session Timed Out",
}


class PanOSAPIError(ConnectionError):
    def __init__(self, api_code):
        self.api_code = api_code

    def __str__(self):
        if self.api_code not in PANOS_API_CODES.keys():
            msg = "UNDOCUMENTED API ERROR CODE"
        else:
            msg = PANOS_API_CODES[self.api_code]

        return repr("{0}: {1}".format(self.api_code, msg))


class PanOSAnsibleModule(AnsibleModule):
    def __init__(
            self,
            argument_spec,
            api_endpoint=None,
            with_state=False,
            with_enabled_state=False,
            *args,
            **kwargs
    ):
        spec = {}

        self.api_endpoint = api_endpoint

        if with_state:
            spec["state"] = {"default": "present", "choices": ["present", "absent"]}

        if with_enabled_state:
            spec["state"] = {
                "default": "present",
                "choices": ["present", "absent", "enabled", "disabled"],
            }

        argument_spec.update(spec)

        super().__init__(argument_spec, *args, **kwargs)

        self.connection = Connection(self._socket_path)


def cmd_xml(cmd):
    def _cmd_xml(args, obj):
        if not args:
            return
        arg = args.pop(0)
        if args:
            result = re.search(r'^"(.*)"$', args[0])
            if result:
                obj.append("<%s>" % arg)
                obj.append(result.group(1))
                obj.append("</%s>" % arg)
                args.pop(0)
                _cmd_xml(args, obj)
            else:
                obj.append("<%s>" % arg)
                _cmd_xml(args, obj)
                obj.append("</%s>" % arg)
        else:
            obj.append("<%s>" % arg)
            _cmd_xml(args, obj)
            obj.append("</%s>" % arg)

    args = cmd.split()
    obj = []
    _cmd_xml(args, obj)
    xml = "".join(obj)

    return xml


def booltostr(b):
    """ Converts a boolean value to a string containing 'yes' or 'no'. """
    if b:
        return "yes"
    else:
        return "no"
