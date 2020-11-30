from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mrichardson03.panos.plugins.modules import panos_address_group

from .common.utils import ModuleTestCase

GET_RESPONSE = {
    "@status": "success",
    "@code": "19",
    "result": {
        "@total-count": "1",
        "@count": "1",
        "entry": [
            {
                "@name": "Test-Group",
                "@location": "vsys",
                "@vsys": "vsys1",
                "static": {"member": ["Test-One", "Test-Two"]},
                "description": "Test Group",
            }
        ],
    },
}


class TestPanosAddressGroup(ModuleTestCase):
    module = panos_address_group

    response = GET_RESPONSE

    create_args = {
        "name": "Test-Group",
        "static_value": ["Test-One", "Test-Two"],
        "description": "Test Group",
    }

    create_result = {
        "@name": "Test-Group",
        "static": {"member": ["Test-One", "Test-Two"]},
        "description": "Test Group",
    }

    modify_args = {
        "name": "Test-Group",
        "static_value": ["Test-One", "Test-Two", "Test-Three"],
        "description": "Test Group",
    }

    modify_result = {
        "@name": "Test-Group",
        "static": {"member": ["Test-One", "Test-Two", "Test-Three"]},
        "description": "Test Group",
    }

    delete_args = {"name": "Test-Group", "state": "absent"}

    def test_create(self, connection_mock):
        connection_mock.send_request.side_effect = [(404, None), (200, None)]

        result = self._run_module(self.create_args)

        assert result["changed"]
        assert result["diff"]["after"] == self.create_result

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
        assert result["diff"]["after"] == self.create_result

    def test_modify(self, connection_mock):
        connection_mock.send_request.side_effect = [(200, self.response), (200, None)]

        result = self._run_module(self.modify_args)

        assert result["changed"]
        assert result["diff"]["after"] == self.modify_result

    def test_modify_fail(self, connection_mock):
        connection_mock.send_request.side_effect = [(200, self.response), (400, None)]

        result = self._run_module_fail(self.modify_args)

        assert "Error editing" in result["msg"]

    def test_delete(self, connection_mock):
        connection_mock.send_request.side_effect = [(200, self.response), (200, None)]

        result = self._run_module(self.delete_args)

        assert result["changed"]
        assert result["diff"]["after"] == ""

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
        assert result["diff"]["before"] == ""
        assert result["diff"]["after"] == ""
