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

# Adapted from:
# https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/wait_for_connection.py


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import xmltodict
from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible_collections.mrichardson03.panos.plugins.httpapi.panos import (
    TimedOutException,
)

display = Display()


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(
        (
            "force",
            "exclude_device_and_network",
            "exclude_policy_and_objects",
            "exclude_shared_objects",
            "description",
            "admins",
            "sleep",
            "timeout",
        )
    )

    DEFAULT_DELAY = 10
    DEFAULT_SLEEP = 10
    DEFAULT_TIMEOUT = 600

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        delay = int(self._task.args.get("delay", self.DEFAULT_DELAY))
        sleep = int(self._task.args.get("sleep", self.DEFAULT_SLEEP))
        timeout = int(self._task.args.get("timeout", self.DEFAULT_TIMEOUT))

        commit_args = dict()
        commit_args["force"] = self._task.args.get("force", False)
        commit_args["exclude_device_and_network"] = self._task.args.get(
            "exclude_device_and_network", False
        )
        commit_args["exclude_policy_and_objects"] = self._task.args.get(
            "exclude_policy_and_objects", False
        )
        commit_args["exclude_shared_objects"] = self._task.args.get(
            "exclude_shared_objects", False
        )
        commit_args["description"] = self._task.args.get("description", None)
        commit_args["admins"] = self._task.args.get("admins", None)

        if self._play_context.check_mode:
            display.vvv("panos_commit: skipping for check_mode")
            return dict(skipped=True)

        result = super().run(tmp, task_vars)
        del tmp  # tmp is unused

        start = datetime.now()

        if delay:
            time.sleep(delay)

        try:
            changes_result = self._connection.op("check pending-changes", is_xml=False)
            changes = ET.fromstring(changes_result).findtext(".//result")

            if changes == "no":
                result["changed"] = False
                result["msg"] = "No changes to commit."
            else:
                commit = self._connection.commit(**commit_args)
                commit_job = ET.fromstring(commit).findtext(".//job")
                display.debug("commit job: {0}".format(commit_job))

                commit_result = self._connection.poll_for_job(
                    commit_job, interval=sleep, timeout=timeout
                )

                result["changed"] = True
                result["stdout"] = json.dumps(xmltodict.parse(commit_result))
                result["stdout_xml"] = commit_result

        except ConnectionError as e:
            result["failed"] = True
            result["msg"] = to_text(e)

        except TimedOutException as e:
            result["failed"] = True
            result["msg"] = to_text(e)

        elapsed = datetime.now() - start
        result["elapsed"] = elapsed.seconds

        self._remove_tmp_path(self._connection._shell.tmpdir)

        result["msg"] = "Commit completed."

        return result
