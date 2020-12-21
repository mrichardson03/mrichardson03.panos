#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Copyright 2020 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: panos_config_element
short_description: Sets arbitrary configuration element in the PAN-OS configuration
description:
    - This module will allow user to pass an xpath and element to be 'set' in the PAN-OS configuration.
author:
    - 'Nathan Embery (@nembery)'
version_added: '1.0.0'
requirements: []

notes:
    - Checkmode is supported.
    - Panorama is supported.
options:
    xpath:
        description:
            - The xpath address where the XML snippet will be inserted into the PAN-OS configuration
        type: str
        required: true
    element:
        description:
            - The XML snippet to be inserted into the PAN-OS configuration
        type: str
        required: true
    override:
        description:
            - Override existing configuration elements if True, otherwise, merge with existing configuration elements
        type: bool
        default: False
        required: false
"""

EXAMPLES = """
- name: configure login banner
  vars:
    banner_text: 'Authorized Personnel Only!'
  panos_config_element:
    xpath: '/config/devices/entry[@name="localhost.localdomain"]/deviceconfig/system'
    element: '<login-banner>{{ banner_text }}</login-banner>'

"""

RETURN = """
diff:
    description: Differences found from existing running configuration and requested element
    returned: success
    type: str
    sample: {"before": "", "after": ""}
"""

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)

try:
    import xmltodict

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            xpath=dict(required=True),
            element=dict(required=True),
            override=dict(type="bool", default=False, required=False),
        ),
        supports_check_mode=True,
    )

    if not HAS_LIB:
        module.fail_json(msg="Missing required libraries.")

    xpath = module.params["xpath"]
    element = module.params["element"]

    override = module.params.get("override", False)

    try:
        existing_response = module.connection.get(xpath)

        existing_object = xmltodict.parse(existing_response)

        existing = existing_object.get("response", {}).get("result", {})

        changed = True

        if __is_present(existing, element) or module.check_mode:
            changed = False

        if changed:
            if override:
                module.connection.edit(xpath, element)
            else:
                module.connection.set(xpath, element)

        diff = {"before": existing_response, "after": element}

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


def __is_present(existing, snippet_string):
    """
    Simple function to check if a snippet is present in the object as returned from the XML API

    :param existing: object as returned from the module.connection.get method
    :param snippet_string: snippet string we want to add
    :return: boolean True if found to be present
    """

    # snippets must not include the surrounding tag info, which means they are not valid XML by themselves
    wrapped_snippet = "<wrapped>" + snippet_string + "</wrapped>"

    # if existing object does not exist, then it can't be present
    if not existing:
        return False

    try:
        snippet = xmltodict.parse(wrapped_snippet)
    except ValueError:
        return False

    return __is_subset(__unwrap(snippet), __unwrap(existing))


def __is_subset(small, large):
    """
    Compare two items to determine if the 'small' item is contained in the 'large' item
    based on answer found here:
    https://stackoverflow.com/questions/44120874/find-if-a-dict-is-contained-in-another-new-version

    :param small: dict, list or str
    :param large: larger dict, list, or str
    :return: true if all items from small are found in large
    """
    if isinstance(small, dict) and isinstance(large, dict):
        for key in small.keys():
            # don't mind extra items added to the candidate config
            # in the normal case, element coming from user will not have these attributes. Can possibly skip this check
            if key in ["@dirtyId", "@admin", "@time"]:
                continue

            if key not in large:
                return False

            elif not __is_subset(small[key], large[key]):
                return False

        return True

    elif isinstance(small, dict) and isinstance(large, list):

        if not any(__is_subset(small, l_item) for l_item in large):
            return False

        return True

    elif isinstance(small, list) and isinstance(large, list):
        for s_item in small:

            if not any(__is_subset(s_item, l_item) for l_item in large):
                return False

        return True

    elif isinstance(small, str):
        if isinstance(large, str):
            return small == large
        elif isinstance(large, dict):
            # The candidate config can do fun things like set an attribute called #text in a dict instead
            # of creating an actual str value
            if "#text" in large:
                return small == large["#text"]

        return False

    # failsafe
    return False


def __unwrap(dict_object):
    """
    Simple function to return the first item found in a given dictionary that does not start with an '@'.
    This is used as xmltodict will return an object with several attributes attached such as @count, @total-count
    etc. The return from the module.connection.get will also 'wrap' the returned items in an extra attribute as well.
    This roughly correlates to the last node in the xpath

    :param dict_object:
    :return:
    """

    for k in dict_object.keys():
        if str(k).startswith("@"):
            continue

        return dict_object[k]


if __name__ == "__main__":
    main()
