from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mrichardson03.panos.plugins.modules import panos_service_object

from .common.utils import ModuleTestCase

GET_RESPONSE = {
    "@status": "success",
    "@code": "19",
    "result": {
        "@total-count": "1",
        "@count": "1",
        "entry": [
            {
                "@name": "ssh-tcp-22",
                "@location": "vsys",
                "@vsys": "vsys1",
                "protocol": {"tcp": {"port": "22", "override": {"no": {}}}},
                "description": "SSH on default port",
            }
        ],
    },
}


class TestPanosServiceObject(ModuleTestCase):
    module = panos_service_object

    response = GET_RESPONSE

    create_args = {
        "name": "ssh-tcp-22",
        "protocol": "tcp",
        "destination_port": "22",
        "description": "SSH on default port",
    }

    created_object = {
        "@name": "ssh-tcp-22",
        "protocol": {"tcp": {"port": "22", "override": {"no": {}}}},
        "description": "SSH on default port",
    }

    modify_args = {
        "name": "ssh-tcp-22",
        "protocol": "tcp",
        "destination_port": "23",
        "description": "Unit tests are fun!",
    }

    delete_args = {"name": "ssh-tcp-22", "state": "absent"}

    def test_create(self, connection_mock):
        connection_mock.send_request.side_effect = [(404, None), (200, None)]

        result = self._run_module(self.create_args)

        assert result["changed"]

    def test_create_fail(self, connection_mock):
        connection_mock.send_request.side_effect = [(404, None), (400, None)]

        result = self._run_module_fail(self.create_args)

        assert "Error creating" in result["msg"]

    def test_create_idempotent(self, connection_mock):
        connection_mock.send_request.side_effect = [
            (200, self.response),
            (200, None),
        ]

        result = self._run_module(self.create_args)

        assert not result["changed"]

    def test_modify(self, connection_mock):
        connection_mock.send_request.side_effect = [(200, self.response), (200, None)]

        result = self._run_module(self.modify_args)

        assert result["changed"]

    def test_modify_fail(self, connection_mock):
        connection_mock.send_request.side_effect = [(200, self.response), (400, None)]

        result = self._run_module_fail(self.modify_args)

        assert "Error editing" in result["msg"]

    def test_delete(self, connection_mock):
        connection_mock.send_request.side_effect = [(200, self.response), (200, None)]

        result = self._run_module(self.delete_args)

        assert result["changed"]

    def test_delete_fail(self, connection_mock):
        connection_mock.send_request.side_effect = [(200, self.response), (400, None)]

        module_args = {"name": "Test-One", "state": "absent"}

        result = self._run_module_fail(module_args)

        assert "Error deleting" in result["msg"]

    def test_delete_absent(self, connection_mock):
        connection_mock.send_request.side_effect = [(404, None), (200, None)]

        module_args = {"name": "Foo", "state": "absent"}

        result = self._run_module(module_args)

        assert not result["changed"]
        assert "does not exist" in result["msg"]

    def test_tcp_override(self, connection_mock):
        connection_mock.send_request.side_effect = [(404, None), (200, None)]

        module_args = {
            "name": "ssh-tcp-22",
            "protocol": "tcp",
            "destination_port": "22",
            "description": "SSH on default port",
            "tcp_override": True,
            "tcp_override_timeout": "111",
            "tcp_override_halfclose_timeout": "222",
            "tcp_override_timewait_timeout": "333",
        }

        created_object = {
            "@name": "ssh-tcp-22",
            "protocol": {
                "tcp": {
                    "port": "22",
                    "override": {
                        "yes": {
                            "timeout": "111",
                            "halfclose-timeout": "222",
                            "timewait-timeout": "333",
                        }
                    },
                }
            },
            "description": "SSH on default port",
        }

        result = self._run_module(module_args)

        print("result = {0}".format(result["object"]))

        assert result["changed"]
        assert result["object"]["entry"] == created_object

    def test_udp_override(self, connection_mock):
        connection_mock.send_request.side_effect = [(404, None), (200, None)]

        module_args = {
            "name": "ssh-udp-22",
            "protocol": "udp",
            "destination_port": "22",
            "description": "SSH on default port",
            "udp_override": True,
            "udp_override_timeout": "111",
        }

        created_object = {
            "@name": "ssh-udp-22",
            "protocol": {
                "udp": {
                    "port": "22",
                    "override": {
                        "yes": {
                            "timeout": "111",
                        }
                    },
                }
            },
            "description": "SSH on default port",
        }

        result = self._run_module(module_args)

        print("result = {0}".format(result["object"]))

        assert result["changed"]
        assert result["object"]["entry"] == created_object
