from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.mrichardson03.panos.plugins.modules import panos_config_element

from .common.utils import ModuleTestCase


class TestPanosConfigElement(ModuleTestCase):
    module = panos_config_element

    def test_existing_element(self, connection_mock):

        element_set = "<some>xml</some>"

        # get will return xml wrapped in last node in xpath, along with possibly other
        # items at the same level
        element_get = "<response><result><xpath><some>xml</some><other_tag>" \
                      "</other_tag></xpath></result></response>"

        connection_mock.get.return_value = element_get

        result = self._run_module({"xpath": "/some/xpath", "element": element_set})

        assert not result["changed"]
        assert result["diff"] == {"before": element_get, "after": element_set}

    def test_changed_element(self, connection_mock):

        existing_element = '<entry name="hi">xml</entry>'
        new_element = '<entry name="hi again">more xml</entry>'

        connection_mock.get.side_effect = [existing_element, new_element]

        connection_mock.set.return_value = (
            200,
            '<response status="success" code="20"><result/></response>',
        )

        result = self._run_module({"xpath": "/some/xpath", "element": new_element})

        assert result["changed"]
