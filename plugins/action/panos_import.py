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

# pylint: skip-file

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import yaml
from ansible.errors import AnsibleActionFail, AnsibleError
from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from yaml.error import YAMLError

display = Display()


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):

        # run default action module first
        result = super(ActionModule, self).run(tmp, task_vars)

        category = self._task.args.get("category")
        filename = self._task.args.get("filename")

        changed = False

        params = {"category": self._task.args.get("category")}

        if category == "certificate" or category == "keypair":
            params["certificate-name"] = self._task.args.get("certificate_name")
            params["format"] = self._task.args.get("format")
            params["passphrase"] = self._task.args.get("passphrase")

        elif category == "custom-logo":
            params["where"] = self._task.args.get("custom_logo_location")

        try:
            if not self._play_context.check_mode:
                real_file_path = self._find_needle("templates", filename)
                self._connection.import_file(real_file_path, category)
                changed = True

        except Exception as e:
            raise AnsibleActionFail(to_text(e))

        result["changed"] = changed
        result["filename"] = filename
        result["msg"] = "okey dokey"
        return result
