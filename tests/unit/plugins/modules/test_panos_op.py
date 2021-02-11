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

from ansible_collections.mrichardson03.panos.plugins.modules import panos_op

from .common.utils import ModuleTestCase


class TestPanosOp(ModuleTestCase):
    module = panos_op

    def test_safe_command(self, connection_mock):
        connection_mock.op.return_value = "<request><result>foo</result></request>"

        result = self._run_module({"cmd": "show system info", "cmd_is_xml": False})

        assert not result["changed"]
        assert result["stdout_xml"] == "<request><result>foo</result></request>"
        assert result["stdout"] == '{"request": {"result": "foo"}}'

    def test_unsafe_command(self, connection_mock):
        connection_mock.op.return_value = "<request><result>foo</result></request>"

        result = self._run_module({"cmd": "request reboot system", "cmd_is_xml": False})

        assert result["changed"]
