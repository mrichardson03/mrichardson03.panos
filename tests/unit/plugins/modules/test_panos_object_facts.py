from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mrichardson03.panos.plugins.modules import panos_object_facts

from .common.utils import (
    ModuleTestCase,
)

GET_ALL = {
    "@status": "success",
    "@code": "19",
    "result": {
        "@total-count": "2",
        "@count": "2",
        "entry": [
            {
                "@name": "Test-One",
                "@location": "vsys",
                "@vsys": "vsys1",
                "ip-netmask": "1.1.1.1",
            },
            {
                "@name": "Test-Two",
                "@location": "vsys",
                "@vsys": "vsys1",
                "ip-netmask": "2.2.2.2",
            },
        ],
    },
}

GET_ALL_RESULT = [
    {
        "@name": "Test-One",
        "@location": "vsys",
        "@vsys": "vsys1",
        "ip-netmask": "1.1.1.1",
    },
    {
        "@name": "Test-Two",
        "@location": "vsys",
        "@vsys": "vsys1",
        "ip-netmask": "2.2.2.2",
    },
]

GET_ONE = {
    "@status": "success",
    "@code": "19",
    "result": {
        "@total-count": "1",
        "@count": "1",
        "entry": [
            {
                "@name": "Test-One",
                "@location": "vsys",
                "@vsys": "vsys1",
                "ip-netmask": "1.1.1.1",
            }
        ],
    },
}

GET_ONE_RESULT = {
    "@name": "Test-One",
    "@location": "vsys",
    "@vsys": "vsys1",
    "ip-netmask": "1.1.1.1",
}


class TestPanosObjectFacts(ModuleTestCase):
    module = panos_object_facts

    def test_get_all(self, connection_mock):
        connection_mock.send_request.return_value = (200, GET_ALL)

        result = self._run_module({"object_type": "address"})

        assert not result["changed"]
        assert result["ansible_module_results"] == GET_ALL_RESULT

    def test_get_one(self, connection_mock):
        connection_mock.send_request.return_value = (200, GET_ONE)

        result = self._run_module({"name": "Test-One", "object_type": "address"})

        assert not result["changed"]
        assert result["ansible_module_results"] == GET_ONE_RESULT
