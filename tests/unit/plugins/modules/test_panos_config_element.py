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

import xml.etree.ElementTree

import pytest
from ansible_collections.paloaltonetworks.panos_enhanced.plugins.modules import (
    panos_config_element,
)
from ansible_collections.paloaltonetworks.panos_enhanced.plugins.modules.panos_config_element import (
    snippets_contained,
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

XPATH_SETTING = (
    "/config/devices/entry[@name='localhost.localdomain']/deviceconfig/setting"
)

SETTING_SNIPPETS = """
<ctd>
  <tcp-bypass-exceed-queue>no</tcp-bypass-exceed-queue>
  <udp-bypass-exceed-queue>no</udp-bypass-exceed-queue>
</ctd>
<management>
  <enable-log-high-dp-load>yes</enable-log-high-dp-load>
  <max-rows-in-csv-export>1048576</max-rows-in-csv-export>
  <api>
    <key>
      <lifetime>525600</lifetime>
    </key>
  </api>
  <admin-lockout>
    <failed-attempts>5</failed-attempts>
    <lockout-time>30</lockout-time>
  </admin-lockout>
  <idle-timeout>10</idle-timeout>
  <auto-acquire-commit-lock>yes</auto-acquire-commit-lock>
</management>
<wildfire>
   <file-size-limit>
    <entry name="pe">
      <size-limit>16</size-limit>
    </entry>
    <entry name="apk">
      <size-limit>30</size-limit>
    </entry>
    <entry name="pdf">
      <size-limit>3072</size-limit>
    </entry>
    <entry name="ms-office">
      <size-limit>16384</size-limit>
    </entry>
    <entry name="jar">
      <size-limit>5</size-limit>
    </entry>
    <entry name="flash">
      <size-limit>5</size-limit>
    </entry>
    <entry name="MacOSX">
      <size-limit>10</size-limit>
    </entry>
    <entry name="archive">
      <size-limit>50</size-limit>
    </entry>
    <entry name="linux">
      <size-limit>50</size-limit>
    </entry>
    <entry name="script">
      <size-limit>2000</size-limit>
    </entry>
   </file-size-limit>
  <report-benign-file>yes</report-benign-file>
  <report-grayware-file>yes</report-grayware-file>
</wildfire>
<config>
  <rematch>yes</rematch>
</config>
<application>
  <notify-user>yes</notify-user>
  <bypass-exceed-queue>no</bypass-exceed-queue>
</application>
<logging>
  <log-suppression>no</log-suppression>
</logging>
<tcp>
  <urgent-data>clear</urgent-data>
  <drop-zero-flag>yes</drop-zero-flag>
  <bypass-exceed-oo-queue>no</bypass-exceed-oo-queue>
  <check-timestamp-option>yes</check-timestamp-option>
  <strip-mptcp-option>yes</strip-mptcp-option>
</tcp>
"""

GET_SETTING = """
<response status="success" code="19">
    <result total-count="1" count="1">
        <setting admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
            <config admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                <rematch admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</rematch>
            </config>
            <management admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                <hostname-type-in-syslog>FQDN</hostname-type-in-syslog>
                <disable-predefined-reports>
                    <member>spyware-infected-hosts</member>
                    <member>top-application-categories</member>
                    <member>top-technology-categories</member>
                    <member>bandwidth-trend</member>
                    <member>risk-trend</member>
                    <member>threat-trend</member>
                    <member>top-users</member>
                    <member>top-attacker-sources</member>
                    <member>top-attacker-destinations</member>
                    <member>top-victim-sources</member>
                    <member>top-victim-destinations</member>
                    <member>top-attackers-by-source-countries</member>
                    <member>top-attackers-by-destination-countries</member>
                    <member>top-victims-by-source-countries</member>
                    <member>top-victims-by-destination-countries</member>
                    <member>top-sources</member>
                    <member>top-destinations</member>
                    <member>top-destination-countries</member>
                    <member>top-source-countries</member>
                    <member>top-connections</member>
                    <member>top-ingress-interfaces</member>
                    <member>top-egress-interfaces</member>
                    <member>top-ingress-zones</member>
                    <member>top-egress-zones</member>
                    <member>top-applications</member>
                    <member>top-http-applications</member>
                    <member>top-rules</member>
                    <member>top-attacks</member>
                    <member>top-spyware-threats</member>
                    <member>top-viruses</member>
                    <member>top-vulnerabilities</member>
                    <member>wildfire-file-digests</member>
                    <member>top-websites</member>
                    <member>top-url-categories</member>
                    <member>top-url-users</member>
                    <member>top-url-user-behavior</member>
                    <member>top-blocked-websites</member>
                    <member>top-blocked-url-categories</member>
                    <member>top-blocked-url-users</member>
                    <member>top-blocked-url-user-behavior</member>
                    <member>blocked-credential-post</member>
                    <member>unknown-tcp-connections</member>
                    <member>unknown-udp-connections</member>
                    <member>top-denied-sources</member>
                    <member>top-denied-destinations</member>
                    <member>top-denied-applications</member>
                    <member>risky-users</member>
                    <member>SaaS Application Usage</member>
                    <member>gtp-events-summary</member>
                    <member>gtp-malicious-wildfire-submissions</member>
                    <member>gtp-security-events</member>
                    <member>gtp-v1-causes</member>
                    <member>gtp-v2-causes</member>
                    <member>gtp-users-visiting-malicious-url</member>
                    <member>top-gtp-attacker-destinations</member>
                    <member>top-gtp-attacker-sources</member>
                    <member>top-gtp-victim-destinations</member>
                    <member>top-gtp-victim-sources</member>
                    <member>sctp-error-causes</member>
                    <member>sctp-events-summary</member>
                    <member>sctp-security-events</member>
                </disable-predefined-reports>
                <enable-log-high-dp-load admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</enable-log-high-dp-load>
                <max-rows-in-csv-export admin="admin" dirtyId="1" time="2021/01/29 11:55:56">1048576</max-rows-in-csv-export>
                <api admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                    <key admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <lifetime admin="admin" dirtyId="1" time="2021/01/29 11:55:56">525600</lifetime>
                    </key>
                </api>
                <admin-lockout admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                    <failed-attempts admin="admin" dirtyId="1" time="2021/01/29 11:55:56">5</failed-attempts>
                    <lockout-time admin="admin" dirtyId="1" time="2021/01/29 11:55:56">30</lockout-time>
                </admin-lockout>
                <idle-timeout admin="admin" dirtyId="1" time="2021/01/29 11:55:56">10</idle-timeout>
                <auto-acquire-commit-lock admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</auto-acquire-commit-lock>
            </management>
            <auto-mac-detect>yes</auto-mac-detect>
            <ctd admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                <tcp-bypass-exceed-queue admin="admin" dirtyId="1" time="2021/01/29 11:55:56">no</tcp-bypass-exceed-queue>
                <udp-bypass-exceed-queue admin="admin" dirtyId="1" time="2021/01/29 11:55:56">no</udp-bypass-exceed-queue>
            </ctd>
            <wildfire admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                <file-size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                    <entry name="pe" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">16</size-limit>
                    </entry>
                    <entry name="apk" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">30</size-limit>
                    </entry>
                    <entry name="pdf" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">3072</size-limit>
                    </entry>
                    <entry name="ms-office" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">16384</size-limit>
                    </entry>
                    <entry name="jar" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">5</size-limit>
                    </entry>
                    <entry name="flash" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">5</size-limit>
                    </entry>
                    <entry name="MacOSX" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">10</size-limit>
                    </entry>
                    <entry name="archive" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">50</size-limit>
                    </entry>
                    <entry name="linux" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">50</size-limit>
                    </entry>
                    <entry name="script" admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                        <size-limit admin="admin" dirtyId="1" time="2021/01/29 11:55:56">2000</size-limit>
                    </entry>
                </file-size-limit>
                <report-benign-file admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</report-benign-file>
                <report-grayware-file admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</report-grayware-file>
            </wildfire>
            <application admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                <notify-user admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</notify-user>
                <bypass-exceed-queue admin="admin" dirtyId="1" time="2021/01/29 11:55:56">no</bypass-exceed-queue>
            </application>
            <logging admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                <log-suppression admin="admin" dirtyId="1" time="2021/01/29 11:55:56">no</log-suppression>
            </logging>
            <tcp admin="admin" dirtyId="1" time="2021/01/29 11:55:56">
                <urgent-data admin="admin" dirtyId="1" time="2021/01/29 11:55:56">clear</urgent-data>
                <drop-zero-flag admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</drop-zero-flag>
                <bypass-exceed-oo-queue admin="admin" dirtyId="1" time="2021/01/29 11:55:56">no</bypass-exceed-oo-queue>
                <check-timestamp-option admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</check-timestamp-option>
                <strip-mptcp-option admin="admin" dirtyId="1" time="2021/01/29 11:55:56">yes</strip-mptcp-option>
            </tcp>
        </setting>
    </result>
</response>
"""

BIG_XML = """
<one>
    <two>
        <three>three text</three>
        <four>four text</four>
    </two>
</one>
"""

SMALL_ONE = "<three>three text</three>"
SMALL_TWO = "<four>four text</four>"

SMALL_THREE = """
<two>
    <three>three text</three>
    <four>four text</four>
</two>
"""


@pytest.mark.parametrize(
    "big_xml,small_xml,result",
    [
        (BIG_XML, SMALL_ONE, True),
        (BIG_XML, SMALL_TWO, True),
        (BIG_XML, SMALL_THREE, True),
        (BIG_XML, "<five/>", False),
        (None, SMALL_ONE, False),
    ],
)
def test_snippets_contained(big_xml, small_xml, result):
    big = xml.etree.ElementTree.fromstring(big_xml) if big_xml else None
    small = xml.etree.ElementTree.fromstring(small_xml)

    assert snippets_contained(big, small) is result


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

    @pytest.mark.parametrize(
        "xpath,element,get_response",
        [
            (XPATH_SYSTEM, COMPLEX_SET, GET_SYSTEM),
        ],
    )
    def test_complex_set_idempotent(
        self, connection_mock, xpath, element, get_response
    ):
        connection_mock.get.return_value = get_response

        args = {"xpath": xpath, "element": element}

        result = self._run_module(args)

        print(result)

        assert result["changed"] is False
