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

from ansible_collections.paloaltonetworks.panos_enhanced.plugins.modules import (
    panos_config_element,
)

from .common.utils import ModuleTestCase

XPATH_ALL = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address"

XPATH_TEST_ONE = "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address/entry[@name='Test-One']"

GET_ADDRESS_EMPTY = """
<response status="success" code="7">
    <result/>
</response>
"""

GET_ADDRESS_TEST_ONE = """
<response status="success" code="19">
    <result total-count="1" count="1">
        <entry name="Test-One">
            <ip-netmask>1.1.1.1</ip-netmask>
        </entry>
    </result>
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

XPATH_SYSTEM = (
    "/config/devices/entry[@name='localhost.localdomain']/deviceconfig/system"
)

GET_EMPTY_SYSTEM = """
<response status="success" code="19">
    <result total-count="1" count="1">
        <system>
            <type>
                <static/>
            </type>
        </system>
    </result>
</response>
"""

SIMPLE_SET = """
<login-banner>You have accessed a protected system.
Log off immediately if you are not an authorized user.</login-banner>
"""

COMPLEX_SET = """
<update-schedule>
    <statistics-service>
        <application-reports>yes</application-reports>
        <threat-prevention-reports>yes</threat-prevention-reports>
        <threat-prevention-pcap>yes</threat-prevention-pcap>
        <threat-prevention-information>yes</threat-prevention-information>
        <passive-dns-monitoring>yes</passive-dns-monitoring>
        <url-reports>yes</url-reports>
        <health-performance-reports>yes</health-performance-reports>
        <file-identification-reports>yes</file-identification-reports>
    </statistics-service>
    <threats>
        <recurring>
        <every-30-mins>
            <at>2</at>
            <action>download-and-install</action>
        </every-30-mins>
        <threshold>48</threshold>
        </recurring>
    </threats>
    <anti-virus>
        <recurring>
        <hourly>
            <at>4</at>
            <action>download-and-install</action>
        </hourly>
        </recurring>
    </anti-virus>
    <wildfire>
        <recurring>
        <every-min>
            <action>download-and-install</action>
        </every-min>
        </recurring>
    </wildfire>
</update-schedule>
<snmp-setting>
    <access-setting>
        <version>
            <v3/>
        </version>
    </access-setting>
</snmp-setting>
<dns-setting>
    <servers>
        <primary>8.8.8.8</primary>
        <secondary>8.8.4.4</secondary>
    </servers>
</dns-setting>
<ntp-servers>
    <primary-ntp-server>
        <ntp-server-address>0.pool.ntp.org</ntp-server-address>
    </primary-ntp-server>
    <secondary-ntp-server>
        <ntp-server-address>1.pool.ntp.org</ntp-server-address>
    </secondary-ntp-server>
</ntp-servers>
<login-banner>You have accessed a protected system.
Log off immediately if you are not an authorized user.</login-banner>
<timezone>UTC</timezone>
"""

GET_SYSTEM = """
<response status="success" code="19">
    <result total-count="1" count="1">
        <system>
            <update-schedule>
                <statistics-service>
                <application-reports>yes</application-reports>
                <threat-prevention-reports>yes</threat-prevention-reports>
                <threat-prevention-pcap>yes</threat-prevention-pcap>
                <threat-prevention-information>yes</threat-prevention-information>
                <passive-dns-monitoring>yes</passive-dns-monitoring>
                <url-reports>yes</url-reports>
                <health-performance-reports>yes</health-performance-reports>
                <file-identification-reports>yes</file-identification-reports>
                </statistics-service>
                <threats>
                <recurring>
                    <every-30-mins>
                    <at>2</at>
                    <action>download-and-install</action>
                    </every-30-mins>
                    <threshold>48</threshold>
                </recurring>
                </threats>
                <anti-virus>
                <recurring>
                    <hourly>
                    <at>4</at>
                    <action>download-and-install</action>
                    </hourly>
                </recurring>
                </anti-virus>
                <wildfire>
                <recurring>
                    <every-min>
                    <action>download-and-install</action>
                    </every-min>
                </recurring>
                </wildfire>
            </update-schedule>
            <snmp-setting>
                <access-setting>
                <version>
                    <v3/>
                </version>
                </access-setting>
            </snmp-setting>
            <dns-setting>
                <servers>
                <primary>8.8.8.8</primary>
                <secondary>8.8.4.4</secondary>
                </servers>
            </dns-setting>
            <ntp-servers>
                <primary-ntp-server>
                <ntp-server-address>0.pool.ntp.org</ntp-server-address>
                </primary-ntp-server>
                <secondary-ntp-server>
                <ntp-server-address>1.pool.ntp.org</ntp-server-address>
                </secondary-ntp-server>
            </ntp-servers>
            <login-banner>You have accessed a protected system.
Log off immediately if you are not an authorized user.</login-banner>
            <timezone>UTC</timezone>
        </system>
    </result>
</response>
"""


class TestPanosConfigElement(ModuleTestCase):
    module = panos_config_element

    def test_create(self, connection_mock):
        connection_mock.get.return_value = GET_ADDRESS_EMPTY

        args = {"xpath": XPATH_TEST_ONE, "element": TEST_ONE, "edit": True}

        result = self._run_module(args)

        assert result["changed"]
        assert connection_mock.edit.call_count == 1

    def test_create_fail(self, connection_mock):
        connection_mock.get.return_value = GET_ADDRESS_EMPTY

        args = {"xpath": XPATH_TEST_ONE, "edit": True}

        result = self._run_module_fail(args)

        assert "'element' is required" in result["msg"]

    def test_create_idempotent(self, connection_mock):
        connection_mock.get.return_value = GET_ADDRESS_TEST_ONE

        args = {"xpath": XPATH_TEST_ONE, "element": TEST_ONE, "edit": True}

        result = self._run_module(args)

        assert not result["changed"]
        assert connection_mock.set.call_count == 0

    def test_modify(self, connection_mock):
        connection_mock.get.return_value = GET_ADDRESS_TEST_ONE

        args = {"xpath": XPATH_TEST_ONE, "element": TEST_ONE_MOD, "edit": True}

        result = self._run_module(args)

        assert result["changed"]
        assert connection_mock.edit.call_count == 1

    def test_delete(self, connection_mock):
        connection_mock.get.return_value = GET_ADDRESS_TEST_ONE

        args = {"xpath": XPATH_TEST_ONE, "state": "absent"}

        result = self._run_module(args)

        assert result["changed"]
        assert connection_mock.delete.call_count == 1

    def test_delete_idempotent(self, connection_mock):
        connection_mock.get.return_value = GET_ADDRESS_EMPTY

        args = {"xpath": XPATH_TEST_ONE, "state": "absent"}

        result = self._run_module(args)

        assert not result["changed"]
        assert connection_mock.delete.call_count == 0

    def test_simple_set(self, connection_mock):
        connection_mock.get.return_value = GET_EMPTY_SYSTEM

        args = {
            "xpath": XPATH_SYSTEM,
            "element": SIMPLE_SET,
        }

        result = self._run_module(args)

        assert result["changed"] is True
        assert connection_mock.set.call_count == 1

    def test_simple_set_modify(self, connection_mock):
        connection_mock.get.return_value = GET_SYSTEM

        args = {"xpath": XPATH_SYSTEM, "element": "<login-banner>foo</login-banner>"}

        result = self._run_module(args)

        assert result["changed"] is True
        assert connection_mock.set.call_count == 1

    def test_complex_set(self, connection_mock):
        connection_mock.get.return_value = GET_EMPTY_SYSTEM

        args = {"xpath": XPATH_SYSTEM, "element": COMPLEX_SET}

        result = self._run_module(args)

        assert result["changed"]

    def test_complex_set_idempotent(self, connection_mock):
        connection_mock.get.return_value = GET_SYSTEM

        args = {"xpath": XPATH_SYSTEM, "element": COMPLEX_SET}

        result = self._run_module(args)

        print(result)

        assert not result["changed"]
