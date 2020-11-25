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
