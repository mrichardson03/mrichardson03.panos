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


class UnauthorizedError(ConnectionError):
    pass


class PanOSAPIError(ConnectionError):
    pass


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

    def apply_state(self, spec):
        state = self.params["state"]

        # Ansible defines all keys, but leaves their value set to None.  Those need
        # cleaned up for comparison.
        spec = remove_dict_empty_keys(spec)

        # Fetch the existing object.
        obj = self.fetch_objects(name=spec["entry"]["@name"])

        # Object will come back from the API with '@location' and '@vsys' keys,
        # but they're not supposed to be in the object spec.
        if obj is not None:
            del obj["@location"]
            del obj["@vsys"]

        changed = False
        diff = None

        if state == "present":

            # Object doesn't exist in the config, it needs to be created.
            if obj is None:

                if not self.check_mode:
                    if not self.add_object(spec):
                        self.fail_json(
                            msg="Error creating object '{0}'".format(
                                spec["entry"]["@name"]
                            )
                        )

                changed = True
                diff = {"before": "", "after": spec["entry"]}

            # An object with that name exists...
            else:

                # There is an object with that name, but it needs modifying.
                if spec["entry"] != obj:

                    if not self.check_mode:
                        if not self.edit_object(spec):
                            self.fail_json(
                                msg="Error editing object '{0}'".format(
                                    spec["entry"]["@name"]
                                )
                            )

                    changed = True
                    diff = {"before": obj, "after": spec["entry"]}

                else:
                    # Object already exists as desired.
                    diff = {"before": obj, "after": spec["entry"]}

        # state == "absent"
        else:

            # Object exists, and needs to be deleted.
            if obj is not None:
                if self.delete_object(spec["entry"]["@name"]) is True:
                    changed = True
                    diff = {"before": obj, "after": ""}

                else:
                    self.fail_json(
                        msg="Error deleting object '{0}'".format(spec["entry"]["@name"])
                    )

            # Object doesn't exist, nothing needs to be done.
            else:
                diff = {"before": "", "after": ""}

        return changed, diff

    def add_object(self, spec):
        params = {"location": "vsys", "vsys": "vsys1", "name": spec["entry"]["@name"]}

        code, data = self.connection.send_request(
            path=self.api_endpoint,
            data=spec,
            method="POST",
            params=params,
            request_type="json",
        )

        if code == 200:
            return True
        else:
            return False

    def edit_object(self, spec):
        params = {"location": "vsys", "vsys": "vsys1", "name": spec["entry"]["@name"]}

        code, data = self.connection.send_request(
            path=self.api_endpoint,
            data=spec,
            method="PUT",
            params=params,
            request_type="json",
        )

        if code == 200:
            return True
        else:
            return False

    def delete_object(self, name):
        params = {"location": "vsys", "vsys": "vsys1", "name": name}

        code, data = self.connection.send_request(
            path=self.api_endpoint, method="DELETE", params=params, request_type="json"
        )

        if code == 200:
            return True
        else:
            return False

    def fetch_objects(self, name=None):
        params = {"location": "vsys", "vsys": "vsys1"}

        if name:
            params.update({"name": name})

        code, data = self.connection.send_request(
            path=self.api_endpoint, method="GET", params=params, request_type="json"
        )

        if code == 200:
            if name:
                return data["result"]["entry"][0]
            else:
                return data["result"]["entry"]
        else:
            return None


def remove_dict_empty_keys(d):
    """
    Remove keys from a dictionary that have values that are either empty
    strings or have 'None' as a value.

    This specifically leaves keys that have values that are empty dictionaries
    ('{}'), because the PAN-OS REST API has some of those.
    """
    new_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = remove_dict_empty_keys(v)
        if v not in (u"", None):
            new_dict[k] = v
    return new_dict


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
