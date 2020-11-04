from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re

from ansible.module_utils.connection import Connection

BASE_HEADERS = {"Content-Type": "application/json"}


def send_request(
    conn,
    data=None,
    path=None,
    method="GET",
    params=None,
    headers=None,
):
    if data and len(data) > 0:
        data = json.dumps(data)

    if headers is None:
        headers = dict(BASE_HEADERS)

    return conn.send_request(
        data, path=path, method=method, params=params, headers=headers
    )


def add_object(conn, spec, api_endpoint):
    params = {"location": "vsys", "vsys": "vsys1", "name": spec["entry"]["@name"]}

    code, data = send_request(
        conn, path=api_endpoint, data=spec, method="POST", params=params
    )

    if code == 200:
        return True
    else:
        return False


def edit_object(conn, spec, api_endpoint):
    params = {"location": "vsys", "vsys": "vsys1", "name": spec["entry"]["@name"]}

    code, data = send_request(
        conn, path=api_endpoint, data=spec, method="PUT", params=params
    )

    if code == 200:
        return True
    else:
        return False


def delete_object(conn, name, api_endpoint):
    params = {"location": "vsys", "vsys": "vsys1", "name": name}

    code, data = send_request(conn, path=api_endpoint, method="DELETE", params=params)

    if code == 200:
        return True
    else:
        return False


def fetch_objects(conn, api_endpoint, name=None):
    params = {"location": "vsys", "vsys": "vsys1"}

    if name:
        params.update({"name": name})

    code, data = send_request(conn, path=api_endpoint, method="GET", params=params)

    if code == 200:
        return data
    else:
        return None


def apply_state(module, spec, api_endpoint=None):
    conn = Connection(module._socket_path)
    state = module.params["state"]

    # Ansible defines all keys, but leaves their value set to None.  Those need
    # cleaned up for comparison.
    spec = remove_dict_empty_keys(spec)

    # Fetch the existing object.
    objs = fetch_objects(conn, spec["entry"]["@name"], api_endpoint)
    obj = None

    if objs is not None:
        obj = objs["result"]["entry"][0]

        # Object will come back from the API with '@location' and '@vsys' keys,
        # but they're not supposed to be in the object spec.
        del obj["@location"]
        del obj["@vsys"]

    if state == "present":

        # Object doesn't exist in the config, it needs to be created.
        if obj is None:

            if not module.check_mode:
                if not add_object(conn, spec, api_endpoint):
                    module.fail_json(
                        msg="Error creating object '{0}'".format(spec["entry"]["@name"])
                    )

            module.exit_json(changed=True, object=spec)

        # An object with that name exists...
        else:
            # There is an object with that name, but it needs modifying.
            if spec["entry"] != obj:

                if not module.check_mode:
                    if not edit_object(conn, spec, api_endpoint):
                        module.fail_json(
                            msg="Error editing object '{0}'".format(
                                spec["entry"]["@name"]
                            )
                        )

                module.exit_json(changed=True, object=spec)

            else:
                # Object already exists as desired.
                module.exit_json(
                    changed=False,
                    msg="Object '{0}' already exists".format(spec["entry"]["@name"]),
                )

    # state == "absent"
    else:

        # Object exists, and needs to be deleted.
        if obj is not None:
            if delete_object(conn, spec["entry"]["@name"], api_endpoint) is True:
                module.exit_json(
                    changed=True,
                    msg="Object '{0}' deleted".format(spec["entry"]["@name"]),
                )
            else:
                module.fail_json(
                    msg="Error deleting object '{0}'".format(spec["entry"]["@name"])
                )

        # Object doesn't exist, nothing needs to be done.
        else:
            module.exit_json(
                changed=False,
                msg="Object '{0}' does not exist".format(spec["entry"]["@name"]),
            )


def remove_dict_empty_keys(d):
    """
    Remove keys from a dictionary that have empty values.
    """
    if type(d) is dict:
        return dict(
            (k, remove_dict_empty_keys(v))
            for k, v in d.items()
            if v and remove_dict_empty_keys(v)
        )
    elif type(d) is list:
        return [remove_dict_empty_keys(v) for v in d if v and remove_dict_empty_keys(v)]
    else:
        return d


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
