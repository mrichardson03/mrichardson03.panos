from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.mrichardson03.panos.plugins.modules import panos_api_key

from .common.utils import (
    ModuleTestCase,
)

GOOD_RESPONSE = (
    200,
    "<request status = 'success'><result><key>foo</key></result></response>",
)


class TestPanosApiKey(ModuleTestCase):
    module = panos_api_key

    @pytest.fixture
    def connection_mock(self, mocker):
        connection_mock = mocker.patch(
            "ansible_collections.mrichardson03.panos.plugins.modules.panos_api_key.Connection"
        )
        return connection_mock.return_value

    def test_api_key_success(self, connection_mock):
        connection_mock.api_key.return_value = "foo"

        result = self._run_module({})

        assert not result["changed"]
        assert result["api_key"] is not None

    def test_api_key_error(self, connection_mock):
        connection_mock.api_key.return_value = None

        result = self._run_module_fail({})

        assert "api_key" not in result
        assert result["msg"] == "Invalid credential"
