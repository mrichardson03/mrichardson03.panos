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

import pytest
from ansible_collections.mrichardson03.panos.plugins.modules import panos_op

from .common.utils import ModuleTestCase

SHOW_JOBS_ID_1 = """
<response status=\"success\">
    <result>
        <job>
            <tenq>2021/05/03 06:52:58</tenq>
            <tdeq>06:52:58</tdeq>
            <id>1</id>
            <user></user>
            <type>AutoCom</type>
            <status>FIN</status>
            <queued>NO</queued>
            <stoppable>no</stoppable>
            <result>OK</result>
            <tfin>06:53:27</tfin>
            <description></description>
            <positionInQ>0</positionInQ>
            <progress>100</progress>
            <details>
                <line>Configuration committed successfully</line>
                <line>Successfully committed last configuration</line>
            </details>
            <warnings></warnings>
        </job>
    </result>
</response>
"""

SHOW_JOBS_ALL_SINGLE = """
<response status=\"success\">
    <result>
        <job>
            <tenq>2021/05/03 06:52:58</tenq>
            <tdeq>06:52:58</tdeq>
            <id>1</id>
            <user></user>
            <type>AutoCom</type>
            <status>FIN</status>
            <queued>NO</queued>
            <stoppable>no</stoppable>
            <result>OK</result>
            <tfin>06:53:27</tfin>
            <description></description>
            <positionInQ>0</positionInQ>
            <progress>100</progress>
            <details>
                <line>Configuration committed successfully</line>
                <line>Successfully committed last configuration</line>
            </details>
            <warnings></warnings>
        </job>
    </result>
</response>
"""

SHOW_JOBS_ALL_MULTI = """
<response status=\"success\">
    <result>
        <job>
            <tenq>2021/05/03 10:18:47</tenq>
            <tdeq>10:18:47</tdeq>
            <id>3</id><user>admin</user>
            <type>WildFire</type>
            <status>FIN</status>
            <queued>NO</queued>
            <stoppable>no</stoppable>
            <result>OK</result>
            <tfin>10:18:52</tfin>
            <description></description>
            <positionInQ>0</positionInQ>
            <progress>10:18:52</progress>
            <details>
                <line>Configuration committed successfully</line>
                <line>Successfully committed last configuration</line>
            </details>
            <warnings></warnings>
        </job>
        <job>
            <tenq>2021/05/03 06:52:58</tenq>
            <tdeq>06:52:58</tdeq>
            <id>1</id>
            <user></user>
            <type>AutoCom</type>
            <status>FIN</status>
            <queued>NO</queued>
            <stoppable>no</stoppable>
            <result>OK</result>
            <tfin>06:53:27</tfin>
            <description></description>
            <positionInQ>0</positionInQ>
            <progress>100</progress>
            <details>
                <line>Configuration committed successfully</line>
                <line>Successfully committed last configuration</line>
            </details>
            <warnings></warnings>
        </job>
    </result>
</response>
"""


class TestPanosOp(ModuleTestCase):
    module = panos_op

    @pytest.mark.parametrize(
        "command,is_xml,changed",
        [
            ("show system info", False, False),
            ("<show><system><info></info></system></show>", True, False),
            ("request reboot system", False, True),
        ],
    )
    def test_safe_commands(self, command, is_xml, changed, connection_mock):
        connection_mock.op.return_value = "<response><result>foo</result></response>"

        result = self._run_module({"cmd": command, "cmd_is_xml": is_xml})

        assert result["changed"] == changed

    def test_job_id(self, connection_mock):
        connection_mock.op.return_value = SHOW_JOBS_ID_1

        result = self._run_module({"job_id": 1})

        assert not result["changed"]

        assert result["job"]["id"] == "1"
        assert result["job"]["result"] == "OK"

    @pytest.mark.parametrize("response", [SHOW_JOBS_ALL_SINGLE, SHOW_JOBS_ALL_MULTI])
    def test_job_type(self, response, connection_mock):
        connection_mock.op.return_value = response

        result = self._run_module({"job_type": "AutoCom"})

        assert not result["changed"]

        assert result["job"]["id"] == "1"
        assert result["job"]["result"] == "OK"

    def test_job_type_not_found(self, connection_mock):
        connection_mock.op.return_value = (
            "<response status='success'><result/></response>"
        )

        result = self._run_module_fail({"job_type": "AutoCom"})

        assert result["msg"] == "Requested job not found."
