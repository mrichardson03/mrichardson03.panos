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

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()

XPATH_BASE = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address"

ELEMENT = """
<entry name="{{ name }}">
    <{{ type }}>{{ value }}</{{ type }}>
{% if description is not none %}
    <description>{{ description }}</description>
{% endif %}
{% if tag %}
    <tag>
        {% for t in tag %}
            <member>{{ t }}</member>
        {% endfor %}
    </tag>
{% endif %}
</entry>
"""


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(["name", "value", "type", "description", "tag", "state"])

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super().run(tmp, task_vars)
        del tmp  # tmp is unused

        plugin_args = {
            "name": self._task.args.get("name", None),
            "value": self._task.args.get("value", None),
            "type": self._task.args.get("type", "ip-netmask"),
            "description": self._task.args.get("description", None),
            "tag": list(self._task.args.get("tag", [])),
        }

        state = self._task.args.get("state", "present")

        # Validate the arguments.
        if plugin_args["name"] is None:
            raise AnsibleError("'name' is required")

        if plugin_args["type"] not in ["ip-netmask", "ip-range", "fqdn"]:
            raise AnsibleError("'type' must be one of 'ip-netmask', 'ip-range', 'fqdn")

        # Calcluate the right xpath.
        xpath = "{0}/entry[@name='{1}']".format(XPATH_BASE, plugin_args["name"])

        # Run our element template through Jinja, using the plugin arguments as
        # variables.
        with self._templar.set_temporary_context(available_variables=plugin_args):
            element = self._templar.do_template(ELEMENT)

        display.vvv("panos_address_object: element = {0}".format(element))

        # Adjust the module arguments based on whether we're adding or deleting
        # an object.
        if state == "present":
            module_args = {"xpath": xpath, "override": True, "element": element}
        else:
            module_args = {"xpath": xpath, "state": "absent"}

        # Make sure we're not in check mode.
        if not self._play_context.check_mode:

            # Call 'panos_config_element' with our new arguments.
            result = self._execute_module(
                module_name="panos_config_element",
                module_args=module_args,
                task_vars=task_vars,
            )

        # Done!
        return result
