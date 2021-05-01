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


class PanOSVersion(object):
    def __init__(self, version):
        try:
            (self.major, self.minor, self.patch) = version.split(".")
            self.xfr = False
        except ValueError:
            (self.major, self.minor, self.patch) = version.split(".")[0:3]
            self.xfr = True

        self.major = int(self.major)
        self.minor = int(self.minor)

    def __eq__(self, other):
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        ):
            return True
        else:
            return False

    def __str__(self):
        s = "{0}.{1}.{2}".format(self.major, self.minor, self.patch)

        if self.xfr:
            s += ".xfr"

        return s


def is_valid_upgrade(current, target):
    # Patch version upgrade (major and minor versions match)
    if (current.major == target.major) and (current.minor == target.minor):
        return True

    # Upgrade minor version (9.0.0 -> 9.1.0)
    elif (current.major == target.major) and (current.minor + 1 == target.minor):
        return True

    # Upgrade major version (9.1.0 -> 10.0.0)
    elif (current.major + 1 == target.major) and (target.minor == 0):
        return True

    else:
        return False


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(
        ["version", "sync_to_peer", "download", "install", "restart", "timeout"]
    )

    def _do_upgrade(
        self,
        current,
        target,
        sync_to_peer=True,
        download=True,
        install=True,
        timeout=600,
    ):
        display.debug(
            "panos_software: performing upgrade ({0} -> {1})".format(current, target)
        )

        cmd = "<request><system><software><check></check></software></system></request>"
        self._connection.op(cmd)

        if download and (
            (current.major != target.major) or (current.minor != target.minor)
        ):
            base = PanOSVersion("{0}.{1}.0".format(target.major, target.minor))
            display.debug("panos_software: download new base version: {0}".format(base))

            cmd = (
                "<request><system><software><download>"
                "<version>{0}</version><sync-to-peer>{1}</sync-to-peer>"
                "</download></software></system></request>".format(
                    base, "yes" if sync_to_peer else "no"
                )
            )

            self._connection.op(cmd, poll=True, poll_interval=10, poll_timeout=timeout)

        if download:
            display.debug("panos_software: download target version: {0}".format(target))

            cmd = (
                "<request><system><software><download>"
                "<version>{0}</version><sync-to-peer>{1}</sync-to-peer>"
                "</download></software></system></request>".format(
                    target, "yes" if sync_to_peer else "no"
                )
            )

            self._connection.op(cmd, poll=True, poll_interval=10, poll_timeout=timeout)

        if install:
            display.debug("panos_software: install target version: {0}".format(target))
            cmd = (
                "<request><system><software><install>"
                "<version>{0}</version>"
                "</install></software></system></request>".format(target)
            )

            self._connection.op(cmd, poll=True, poll_interval=10, poll_timeout=timeout)

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super().run(tmp, task_vars)
        del tmp

        if "version" not in self._task.args:
            raise AnsibleError("'version' is required")

        target = PanOSVersion(self._task.args.get("version"))
        sync_to_peer = bool(self._task.args.get("sync_to_peer", True))
        download = bool(self._task.args.get("download", True))
        install = bool(self._task.args.get("install", True))
        restart = bool(self._task.args.get("restart", False))
        timeout = int(self._task.args.get("timeout", 600))

        current = PanOSVersion(self._connection.version()["sw-version"])

        if target != current:
            result["changed"] = True
            result["msg"] = "Installed PAN-OS version {0}.".format(target)

            if not is_valid_upgrade(current, target):
                raise AnsibleError(
                    "upgrade is invalid: ({0} -> {1})".format(current, target)
                )

            if not self._play_context.check_mode:
                self._do_upgrade(
                    current,
                    target,
                    sync_to_peer=sync_to_peer,
                    download=download,
                    install=install,
                )

            if restart:
                display.debug("panos_software: restarting device")

                if not self._play_context.check_mode:
                    self._connection.op("request restart system", is_xml=False)

        return result
