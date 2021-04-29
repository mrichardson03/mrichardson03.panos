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


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time

import xmltodict
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(["authcode"])

    def _apply_authcode(self, authcode):
        """Activates features using an authcode."""
        cmd = "<request><license><fetch><auth-code>{0}</auth-code></fetch></license></request>".format(
            authcode
        )

        # Catch any exceptions here because things get weird when the management
        # plane restarts.
        try:
            result = self._connection.op(cmd, validate=False)
        except Exception:
            pass

        if "already provisioned" not in to_text(result):
            return True
        else:
            return False

    def _fetch_licenses(self):
        """Retrieves info on licensees."""
        cmd = "request license info"

        try:
            result = self._connection.op(cmd, is_xml=False)
        except Exception as e:
            raise AnsibleError("Error retreiving license info.") from e

        parsed = xmltodict.parse(result, force_list=("entry,"))
        licenses = parsed.get("response").get("result").get("licenses", None)

        if licenses is None:
            return []
        else:
            return parsed.get("response").get("result").get("licenses").get("entry", [])

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super().run(tmp, task_vars)
        del tmp

        authcode = self._task.args.get("authcode", None)

        if authcode:
            if self._apply_authcode(authcode):
                # Activating a VM license causes a management plane restart.
                # Sleep for a completely unscientific amount of time,
                # then see if the autocommit has succeeded.
                time.sleep(600)

                self._execute_module(
                    module_name="mrichardson03.panos.panos_check",
                    task_vars=task_vars,
                )

                result["changed"] = True

        version = self._connection.version(refresh=True)

        result["serial"] = version["serial"]
        result["licenses"] = self._fetch_licenses()

        return result
