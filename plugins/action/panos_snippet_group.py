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
    @staticmethod
    def _extract_snippet_group_variables(snippet_group_def):
        """
        Takes a snippet_group_def as loaded from the snippet group YAML and
        extracts all the variables along with their default values.

        These are added to the task_vars so the user does not have to set all
        values in the task.

        :param snippet_group_def: dict as loaded from the YAML definition file
        :return: dict of variable key/value pairs
        """

        display.vvv("snippet_group_def is")
        display.vvv(str(snippet_group_def))

        variables_list = snippet_group_def.get("variables", [])

        display.vvv(str(variables_list))

        task_var_defaults = dict()
        for v in variables_list:
            var_name = v["name"]
            var_default = v["default"]

            task_var_defaults[var_name] = var_default

        return task_var_defaults

    def run(self, tmp=None, task_vars=None):

        # run default action module first
        result = super(ActionModule, self).run(tmp, task_vars)

        source = self._task.args.get("src", None)

        try:
            src_file = self._find_needle("templates", source)
        except AnsibleError as e:
            raise AnsibleActionFail(to_text(e))

        with open(src_file, "rb") as f:
            try:
                src_file_data = to_text(f.read(), errors="surrogate_or_strict")

                snippet_group = yaml.safe_load(src_file_data)

            except UnicodeError:
                raise AnsibleActionFail("Source files must be utf-8 encoded")
            except YAMLError:
                raise AnsibleActionFail("Could not load Snippets file")

        if "snippets" not in snippet_group:
            raise AnsibleActionFail("Could not load Snippets file")

        # grab the default values from the snippet_group definition
        task_var_defaults = self._extract_snippet_group_variables(snippet_group)

        # allow user to override any variable defined therein via the task_vars
        task_var_defaults.update(task_vars)

        for snippet in snippet_group["snippets"]:
            snippet_name = snippet.get("name", None)
            xpath_tpl = snippet.get("xpath", None)
            element_tpl = snippet.get("element", None)
            cmd = snippet.get("cmd", "set")

            if cmd == "edit":
                override = True
            else:
                override = False

            with self._templar.set_temporary_context(
                available_variables=task_var_defaults
            ):
                xpath = self._templar.do_template(xpath_tpl)
                element = self._templar.do_template(element_tpl)

                display.vvv("xpath is now: {0}".format(xpath))
                display.vvv("element is now: {0}".format(element))

                module_args = {"xpath": xpath, "element": element, "override": override}

                snippet_result = self._execute_module(
                    module_name="panos_config_element",
                    module_args=module_args,
                    task_vars=task_var_defaults,
                )

                result[snippet_name] = snippet_result
                display.vvv(str(snippet_result))

                if snippet_result.get("changed", True):
                    result["changed"] = True

        return result
