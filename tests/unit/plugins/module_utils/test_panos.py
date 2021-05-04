from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    cmd_xml,
    get_nested_key,
)


def test_cmd_xml():
    show_system_info = "<show><system><info></info></system></show>"
    show_interface_all = "<show><interface>all</interface></show>"

    assert cmd_xml("show system info") == show_system_info
    assert cmd_xml('show interface "all"') == show_interface_all


@pytest.mark.parametrize(
    "key_list,expected", [(["one", "two", "three"], "four"), (["five"], None)]
)
def test_get_nested_key(key_list, expected):
    d = {"one": {"two": {"three": "four"}}}

    assert get_nested_key(d, key_list) == expected
