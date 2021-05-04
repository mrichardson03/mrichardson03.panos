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

import pytest
from ansible_collections.mrichardson03.panos.plugins.modules import panos_op

from .common.utils import ModuleTestCase


class TestPanosOp(ModuleTestCase):
    module = panos_op

    @pytest.mark.parametrize(
        "command,is_xml,changed",
        [
            ("show system info", False, False),
            ("<show><system><info></info></system></show>", True, False),
            ("request reboot system", False, True),
        ],
    )
    def test_safe_commands(self, command, is_xml, changed, connection_mock):
        connection_mock.op.return_value = "<response><result>foo</result></response>"

        result = self._run_module({"cmd": command, "cmd_is_xml": is_xml})

        assert result["changed"] == changed
