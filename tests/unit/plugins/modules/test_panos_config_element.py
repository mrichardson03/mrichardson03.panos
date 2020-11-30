from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mrichardson03.panos.plugins.modules import panos_config_element

<<<<<<< HEAD
from .common.utils import (
    ModuleTestCase,
)
=======
from .common.utils import ModuleTestCase
>>>>>>> upstream/develop


class TestPanosConfigElement(ModuleTestCase):
    module = panos_config_element

    def test_existing_element(self, connection_mock):

<<<<<<< HEAD
        element = '<some>xml</some>'
=======
        element = "<some>xml</some>"
>>>>>>> upstream/develop
        connection_mock.get.return_value = element

        result = self._run_module({"xpath": "/some/xpath", "element": element})

        assert not result["changed"]
        assert result["diff"] == {"before": element, "after": element}

    def test_changed_element(self, connection_mock):

        existing_element = '<entry name="hi">xml</entry>'
        new_element = '<entry name="hi again">more xml</entry>'

        connection_mock.get.side_effect = [existing_element, new_element]
<<<<<<< HEAD
        connection_mock.set.return_value = 200, '<response status="success" code="20"><result/></response>'
=======
        connection_mock.set.return_value = (
            200,
            '<response status="success" code="20"><result/></response>',
        )
>>>>>>> upstream/develop

        result = self._run_module({"xpath": "/some/xpath", "element": new_element})

        assert result["changed"]
