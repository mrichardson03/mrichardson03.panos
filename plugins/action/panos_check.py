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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time
import xml.etree.ElementTree
from datetime import datetime, timedelta

from ansible.module_utils._text import to_text
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


class TimedOutException(Exception):
    pass


def check_autocommit(jobs):
    if len(jobs) == 0:
        return False

    for j in jobs:
        job_type = j.findtext(".//type")
        job_result = j.findtext(".//result")

        if job_type is None or job_result is None:
            return False

        if job_type == "AutoCom" and job_result == "OK":
            return True
        elif job_type == "AutoCom":
            return False

    # If we get to this point, the autocommit job is no longer in the job
    # history and it is assumed the device is ready.
    return True


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(("delay", "sleep", "timeout"))

    DEFAULT_DELAY = 0
    DEFAULT_SLEEP = 60
    DEFAULT_TIMEOUT = 600

    def do_until_success_or_timeout(self, timeout, sleep):
        max_end_time = datetime.utcnow() + timedelta(seconds=timeout)

        while datetime.utcnow() < max_end_time:
            try:
                result = self._connection.op("show jobs all")
                jobs = xml.etree.ElementTree.fromstring(result).findall(".//job")
                display.debug(jobs)
                if check_autocommit(jobs):
                    display.debug("panos_check: success")
                    return
                else:
                    display.debug(
                        "panos_check: autocommit not completed, retrying in {0} seconds".format(
                            sleep
                        )
                    )
                    time.sleep(sleep)
            except Exception:
                display.debug(
                    "panos_check: connection error (expected), retrying in {0} seconds".format(
                        sleep
                    )
                )
                time.sleep(sleep)

        raise TimedOutException("Timed out waiting for autocommit to complete.")

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        delay = int(self._task.args.get("delay", self.DEFAULT_DELAY))
        sleep = int(self._task.args.get("sleep", self.DEFAULT_SLEEP))
        timeout = int(self._task.args.get("timeout", self.DEFAULT_TIMEOUT))

        if self._play_context.check_mode:
            display.vvv("panos_check: skipping for check_mode")
            return dict(skipped=True)

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp

        start = datetime.now()

        if delay:
            time.sleep(delay)

        try:
            self.do_until_success_or_timeout(timeout, sleep)

        except TimedOutException as e:
            result["failed"] = True
            result["msg"] = to_text(e)

        elapsed = datetime.now() - start
        result["elapsed"] = elapsed.seconds

        self._remove_tmp_path(self._connection._shell.tmpdir)

        result["msg"] = "Autocommit completed."

        return result
