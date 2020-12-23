from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from unittest import mock

import pytest
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.six import BytesIO, StringIO
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible_collections.mrichardson03.panos.plugins.httpapi.panos import HttpApi

GOOD_KEYGEN = """
<response><result><key>foo</key></result></response>
"""

BAD_KEYGEN = """
<response><result><msg>Invalid Credential</msg></result></response>
"""

SHOW_SYSTEM_INFO_RESPONSE = """
<response status=\"success\">
    <result>
        <system>
            <hostname>PA-VM</hostname>
            <uptime>0 days, 0:57:35</uptime>
            <model>PA-VM</model>
            <serial>015351000039218</serial>
            <sw-version>10.0.0</sw-version>
            <uptime>uptime</uptime>
            <multi-vsys>multivsys</multi-vsys>
        </system>
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

    def test_login_success(self):
        self.connection_mock.send.return_value = self._connection_response(
            GOOD_KEYGEN, status=200
        )

        self.plugin.login("USERNAME", "PASSWORD")

        assert self.plugin.api_key() == "foo"

    def test_login_fail(self):
        self.connection_mock.send.return_value = self._connection_response(
            BAD_KEYGEN, status=401
        )

        with pytest.raises(AnsibleConnectionFailure) as res:
            self.plugin.login("USERNAME", "PASSWORD")

        assert "Invalid credential" in str(res.value)
        assert self.plugin.api_key() is None

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

    def test_handle_http_error(self):
        self.connection_mock.send.side_effect = HTTPError(
            "http://testhost.com", 500, "", {}, StringIO('{"errorMessage": "ERROR"}')
        )

        code, response = self.plugin.send_request(None, path="/nonexistent")
        assert code == 500

    def test_handle_httperror_retry_login(self):
        response_mock = mock.Mock()
        type(response_mock).code = mock.PropertyMock(return_value=401)

        with mock.patch.object(HttpApi, "login", return_value=None) as mock_login:
            retval = self.plugin.handle_httperror(response_mock)

        assert mock_login.call_count == 1
        assert retval is True

    def test_handle_httperror_auth_error(self):
        response_mock = mock.Mock()
        type(response_mock).code = mock.PropertyMock(return_value=401)
        type(self.connection_mock)._auth = mock.PropertyMock(return_value=None)

        with mock.patch.object(HttpApi, "login", return_value=None) as mock_login:
            retval = self.plugin.handle_httperror(response_mock)

        assert mock_login.call_count == 0
        assert retval is False

    def test_handle_httperror_404(self):
        response_mock = mock.Mock()
        type(response_mock).code = mock.PropertyMock(return_value=404)

        assert self.plugin.handle_httperror(response_mock) is False

    @staticmethod
    def _connection_response(response, status=200):
        response_mock = mock.Mock()
        response_mock.getcode.return_value = status
        response_text = json.dumps(response) if type(response) is dict else response
        response_data = BytesIO(
            response_text.encode() if response_text else "".encode()
        )
        return response_mock, response_data
