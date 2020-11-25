from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mrichardson03.panos.plugins.modules import panos_commit

from .common.utils import ModuleTestCase


class TestPanosOp(ModuleTestCase):
    module = panos_commit

    def test_no_changes(self, connection_mock):
        connection_mock.op.return_value = "<request><result>no</result></request>"

        result = self._run_module({})

        assert not result["changed"]
        assert connection_mock.commit.call_count == 0

    def test_no_job_id(self, connection_mock):
        connection_mock.op.return_value = "<request><result>yes</result></request>"
        connection_mock.commit.return_value = (
            "<request><msg>No job id here</msg></request>"
        )

        result = self._run_module_fail({})

        assert "Could not find commit job" in result["msg"]

    def test_commit_fail(self, connection_mock):
        connection_mock.op.return_value = "<request><result>yes</result></request>"
        connection_mock.commit.return_value = (
            "<request><result><job>2</job></result></request>"
        )
        connection_mock.poll_for_job.return_value = (
            "<request><result><job><result>FAIL</result></job></result></request>"
        )

        self._run_module_fail({})

    def test_commit_succeed(self, connection_mock):
        connection_mock.op.return_value = "<request><result>yes</result></request>"
        connection_mock.commit.return_value = (
            "<request><result><job>2</job></result></request>"
        )
        connection_mock.poll_for_job.return_value = (
            "<request><result><job><result>OK</result></job></result></request>"
        )

        result = self._run_module({})

        assert result["changed"]

    # def test_safe_command(self, connection_mock):
    #     connection_mock.op.return_value = "<request><result>foo</result></request>"

    #     result = self._run_module({"cmd": "show system info", "cmd_is_xml": False})

    #     assert not result["changed"]
    #     assert result["stdout_xml"] == "<request><result>foo</result></request>"
    #     assert result["stdout"] == '{"request": {"result": "foo"}}'

    # def test_unsafe_command(self, connection_mock):
    #     connection_mock.op.return_value = "<request><result>foo</result></request>"

    #     result = self._run_module({"cmd": "request reboot system", "cmd_is_xml": False})

    #     assert result["changed"]
