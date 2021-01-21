from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest import mock
from unittest.mock import patch

import pytest
from ansible.module_utils.six import BytesIO
from ansible_collections.mrichardson03.panos.plugins.httpapi.panos import HttpApi

GOOD_KEYGEN = """
<response><result><key>foo</key></result></response>
"""

BAD_KEYGEN = """
<response><result><msg>Invalid Credential</msg></result></response>
"""

VERSION = """
<response status = "success">
    <result>
        <sw-version>10.0.2</sw-version>
        <multi-vsys>off</multi-vsys>
        <model>PA-VM</model>
        <serial>007000001222</serial>
    </result>
</response>
"""


class FakeHttpApiPlugin(HttpApi):
    def __init__(self, connection):
        super().__init__(connection)

        self.hostvars = {"api_key": None}

    def get_option(self, var):
        return self.hostvars[var]

    def set_option(self, var, val):
        self.hostvars[var] = val


class TestPanosHttpApi:
    def setup_method(self, method):
        self.connection_mock = mock.Mock()
        self.plugin = FakeHttpApiPlugin(self.connection_mock)

    @patch.object(HttpApi, "keygen")
    def test_api_key_generate(self, mock_keygen):
        self.connection_mock.get_option.side_effect = ["USERNAME", "PASSWORD"]
        mock_keygen.return_value = "foo"

        ret_value = self.plugin.api_key()

        assert ret_value == "foo"

    def test_api_key_specified(self):
        self.plugin.set_option("api_key", "foo")

        ret_value = self.plugin.api_key()

        assert ret_value == "foo"

    @pytest.mark.parametrize(
        "response,status,expected",
        [(GOOD_KEYGEN, 200, "foo"), (BAD_KEYGEN, 401, None)],
    )
    def test_keygen(self, response, status, expected):
        self.connection_mock.send.return_value = self._connection_response(
            response,
            status=status,
        )

        key = self.plugin.keygen("USERNAME", "PASSWORD")

        assert key == expected

    @patch.object(HttpApi, "api_key")
    @patch.object(HttpApi, "send_request")
    def test_version(self, mock_send_request, mock_api_key):
        mock_send_request.return_value = (200, VERSION)
        mock_api_key.return_value = "foo"

        ret_value = self.plugin.version()

        assert ret_value["sw-version"] == "10.0.2"

    @pytest.mark.parametrize(
        "http_status,http_response",
        [(200, "<request status='success'></request>")],
    )
    def test_validate_response(self, http_status, http_response):
        response = self.plugin._validate_response(http_status, http_response)

        assert response == http_response

    @pytest.mark.parametrize("http_status,http_response", [(401, None)])
    def test_validate_response_connection_error(self, http_status, http_response):
        with pytest.raises(ConnectionError):
            self.plugin._validate_response(http_status, http_response)

    @pytest.mark.parametrize(
        "http_status,http_response",
        [
            (200, "<request status='error' code='1'></request>"),
            (403, "<request status='error' code='403'></request>"),
        ],
    )
    def test_validate_response_api_exception(self, http_status, http_response):
        with pytest.raises(ConnectionError):
            self.plugin._validate_response(http_status, http_response)

    @staticmethod
    def _connection_response(response, status=200):
        response_mock = mock.Mock()
        response_mock.getcode.return_value = status
        response_text = response
        response_data = BytesIO(
            response_text.encode() if response_text else "".encode()
        )
        return response_mock, response_data
