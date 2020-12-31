#!/usr/bin/python

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

DOCUMENTATION = """
---
module: panos_config_element
short_description: Modifies an element in the PAN-OS configuration.
description:
    - This module allows the user to modify an element in the PAN-OS configuration
      by specifying an element and its location in the configuration (xpath).
author:
    - 'Nathan Embery (@nembery)'
    - 'Michael Richardson (@mrichardson03)'
version_added: '1.0.0'
requirements: []
notes:
    - Checkmode is supported.
    - Panorama is supported.
extends_documentation_fragment:
    - mrichardson03.panos.fragments.state
options:
    xpath:
        description:
            - Location of the specified element in the XML configuration.
        type: str
        required: true
    element:
        description:
            - The element, in XML format.
        type: str
    override:
        description:
            - If **true**, override any existing configuration at the specified
              location with the contents of *element*.
            - If **false**, merge the contents of *element* with any existing
              configuration at the specified location.
        type: bool
        default: False
        required: false
"""

EXAMPLES = """
- name: Configure login banner
  vars:
    banner_text: 'Authorized Personnel Only!'
  panos_config_element:
    xpath: '/config/devices/entry[@name="localhost.localdomain"]/deviceconfig/system'
    element: '<login-banner>{{ banner_text }}</login-banner>'

- name: Create address object
  panos_config_element:
    xpath: "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address"
    element: |
      <entry name="Test-One">
        <ip-netmask>1.1.1.1</ip-netmask>
      </entry>

- name: Delete address object 'Test-One'
  panos_config_element:
    xpath: "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address/entry[@name='Test-One']"
    state: 'absent'
"""

RETURN = """
changed:
    description: A boolean value indicating if the task had to make changes.
    returned: always
    type: bool
msg:
    description: A string with an error message, if any.
    returned: failure, always
    type: str
diff:
    description:
        - Information about the differences between the previous and current
          state.
        - Contains 'before' and 'after' keys.
    returned: success, when needed
    type: dict
    elements: str
"""

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)

try:
    import xmltodict

    HAS_LIB = True
except ImportError:  # pragma: no cover
    HAS_LIB = False


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            xpath=dict(required=True),
            element=dict(required=False),
            override=dict(type="bool", default=False, required=False),
        ),
        supports_check_mode=True,
        with_state=True,
    )

    if not HAS_LIB:  # pragma: no cover
        module.fail_json(msg="Missing required libraries.")

    xpath = module.params["xpath"]
    element = module.params["element"]
    override = module.params["override"]
    state = module.params["state"]

    try:
        existing_response = module.connection.get(xpath)
        existing_object = xmltodict.parse(existing_response)

        existing = existing_object.get("response", {}).get("result", {})

        changed = False
        diff = {}

        if state == "present":
            if element is None:
                module.fail_json(msg="'element' is required when state is 'present'.")

            # Element does not exist as desired, create/edit it.
            if not __is_present(existing, element):
                changed = True

                if not module.check_mode:
                    if override:
                        module.connection.edit(xpath, element)
                    else:
                        module.connection.set(xpath, element)

            # Element exists as desired.
            diff = {"before": existing_response, "after": element}

        # state == "absent"
        else:
            # Element exists, delete it.
            if existing is not None:
                changed = True

                if not module.check_mode:
                    module.connection.delete(xpath)

                diff = {"before": existing_response, "after": ""}

            # Element doesn't exist, nothing needs to be done.
            else:
                diff = {"before": "", "after": ""}

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:  # pragma: no cover
        module.fail_json(msg="{0}".format(e))


def __is_present(existing, snippet_string):
    """
    Simple function to check if a snippet is present in the object as returned
    from the XML API.

    :param existing: object as returned from the module.connection.get method
    :param snippet_string: snippet string we want to add
    :return: boolean True if found to be present
    """

    # snippets must not include the surrounding tag info, which means they are
    # not valid XML by themselves
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
    Compare two items to determine if the 'small' item is contained in the
    'large' item.

    Based on answer found here:
    https://stackoverflow.com/questions/44120874/find-if-a-dict-is-contained-in-another-new-version

    :param small: dict, list or str
    :param large: larger dict, list, or str
    :return: true if all items from small are found in large
    """
    if isinstance(small, dict) and isinstance(large, dict):
        for key in small.keys():
            # don't mind extra items added to the candidate config
            # in the normal case, element coming from user will not have these
            # attributes. Can possibly skip this check.
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
            # The candidate config can do fun things like set an attribute
            # called #text in a dict instead of creating an actual str value
            if "#text" in large:
                return small == large["#text"]

        return False

    elif small is None and isinstance(large, dict):
        # handle cases where we have a bare tag in the candidate config
        # then candidate will only contain the metadata attributes
        # todo: is there a better way to do this?
        if list(large.keys()).sort() == ["@dirtyId", "@admin", "@time"].sort():
            return True

    # failsafe
    return False


def __unwrap(dict_object):
    """
    Simple function to return the first item found in a given dictionary that
    does not start with an '@'.

    This is used as xmltodict will return an object with several attributes
    attached such as @count, @total-count etc. The return from
    module.connection.get will also 'wrap' the returned items in an extra
    attribute as well.

    This roughly correlates to the last node in the xpath.

    :param dict_object:
    :return:
    """

    for k in dict_object.keys():
        if str(k).startswith("@"):
            continue

        return dict_object[k]


if __name__ == "__main__":  # pragma: no cover
    main()
