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

from ansible_collections.mrichardson03.panos.plugins.modules import panos_config_element

from .common.utils import ModuleTestCase

XPATH_ALL = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address"

GET_ALL_EMPTY = """
<response status="success">
    <result>
        <address/>
    </result>
</response>
"""

GET_ALL_TEST_ONE = """
<response status="success">
    <result>
        <address>
            <entry name="Test-One">
                <ip-netmask>1.1.1.1</ip-netmask>
            </entry>
        </address>
    </result>
</response>
"""

XPATH_TEST_ONE = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address/entry[@name='Test-One']"

GET_TEST_ONE = """
<response status="success" code="19">
    <result total-count="1" count="1">
        <entry name="Test-One" admin="admin" dirtyId="3" time="2020/12/31 11:44:20">
            <ip-netmask admin="admin" dirtyId="3" time="2020/12/31 11:44:20">1.1.1.1</ip-netmask>
        </entry>
    </result>
</response>
"""

GET_TEST_ONE_EMPTY = """
<response status="success" code="7">
    <result/>
</response>
"""

TEST_ONE = """
<entry name="Test-One">
    <ip-netmask>1.1.1.1</ip-netmask>
</entry>
"""

TEST_ONE_MOD = """
<entry name="Test-One">
    <ip-netmask>2.2.2.2</ip-netmask>
</entry>
"""

TEST_TWO = """
<entry name="Test-Two">
    <ip-netmask>2.2.2.2</ip-netmask>
</entry>
"""


class TestPanosConfigElement(ModuleTestCase):
    module = panos_config_element

    def test_create(self, connection_mock):
        connection_mock.get.return_value = GET_ALL_EMPTY

        args = {"xpath": XPATH_ALL, "element": TEST_ONE}

        result = self._run_module(args)

        assert result["changed"]
        assert connection_mock.set.call_count == 1

    def test_create_fail(self, connection_mock):
        connection_mock.get.return_value = GET_ALL_EMPTY

        args = {"xpath": XPATH_ALL}

        result = self._run_module_fail(args)

        assert "'element' is required" in result["msg"]

    def test_create_idempotent(self, connection_mock):
        connection_mock.get.return_value = GET_ALL_TEST_ONE

        args = {"xpath": XPATH_ALL, "element": TEST_ONE}

        result = self._run_module(args)

        assert not result["changed"]
        assert connection_mock.set.call_count == 0

    def test_modify(self, connection_mock):
        connection_mock.get.return_value = GET_TEST_ONE

        args = {"xpath": XPATH_TEST_ONE, "element": TEST_ONE_MOD, "override": True}

        result = self._run_module(args)

        assert result["changed"]
        assert connection_mock.edit.call_count == 1

    def test_delete(self, connection_mock):
        connection_mock.get.return_value = GET_TEST_ONE

        args = {"xpath": XPATH_TEST_ONE, "state": "absent"}

        result = self._run_module(args)

        assert result["changed"]
        assert connection_mock.delete.call_count == 1

    def test_delete_idempotent(self, connection_mock):
        connection_mock.get.return_value = GET_TEST_ONE_EMPTY

        args = {"xpath": XPATH_TEST_ONE, "state": "absent"}

        result = self._run_module(args)

        assert not result["changed"]
        assert connection_mock.delete.call_count == 0
