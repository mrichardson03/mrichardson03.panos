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
    edit:
        description:
            - If **true**, replace any existing configuration at the specified
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

import xml.etree.ElementTree

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def xml_compare(one, two, excludes=None):
    """
    Compares the contents of two xml.etree.ElementTrees for equality.

    :param one: First ElementTree.
    :param two: Second ElementTree.
    :param excludes: List of tag attributes to disregard.
    """
    if excludes is None:
        excludes = ["admin", "dirtyId", "time", "uuid"]

    if one is None or two is None:
        return False

    if one.tag != two.tag:
        # Tag does not match.
        return False

    # Compare attributes.
    for name, value in one.attrib.items():
        if name not in excludes:
            if two.attrib.get(name) != value:
                return False

    for name, value in two.attrib.items():
        if name not in excludes:
            if one.attrib.get(name) != value:
                return False

    if not text_compare(one.text, two.text):
        # Text differs at this node.
        return False

    # Sort children by tag name to make sure they're compared in order.
    children_one = sorted(one, key=lambda e: e.tag)
    children_two = sorted(two, key=lambda e: e.tag)

    if len(children_one) != len(children_two):
        # Number of children differs.
        return False

    for child_one, child_two in zip(children_one, children_two):
        if not xml_compare(child_one, child_two, excludes):
            # Child documents do not match.
            return False

    return True


def text_compare(one, two):
    """Compares the contents of two XML text attributes."""
    if not one and not two:
        return True
    return (one or "").strip() == (two or "").strip()


def iterpath(node, tag=None, path="."):
    """
    Similar to Element.iter(), but the iterator gives each element's path along
    with the element itself.

    Reference: https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element.iter

    Taken from: https://stackoverflow.com/questions/13136334/get-xpath-dynamically-using-elementtree-getpath
    """
    if tag == "*":
        tag = None

    if tag is None or node.tag == tag:
        yield node, path

    for child in node:
        if child.tag == "entry":
            _child_path = "{0}/{1}[@name='{2}']".format(
                path, child.tag, child.attrib["name"]
            )
        else:
            _child_path = "{0}/{1}".format(path, child.tag)

        for child, child_path in iterpath(child, tag, path=_child_path):
            yield child, child_path


def xml_contained(big, small):
    """
    Check to see if all the XML elements with no children in "small" are
    present in "big", at the same locations in the tree.

    This ensures all the configuration in "small" is contained in "big", but
    "big" can have configuration not contained in "small".

    :param big: Big document ElementTree.
    :param small: Small document ElementTree.
    """

    if big is None or small is None:
        return False

    for element, path in iterpath(small):

        # Elements with "member" children must have all their children be equal.
        if element.find("*/member/..") is not None:
            big_element = big.find(path)

            if not xml_compare(big_element, element):
                return False

        # Elements with no children at the same point in the tree must match
        # exactly.
        elif len(element) == 0 and (element.tag != "member"):
            big_element = big.find(path)

            if not xml_compare(big_element, element):
                return False

    return True


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            xpath=dict(required=True),
            element=dict(required=False),
            edit=dict(type="bool", default=False, required=False),
        ),
        supports_check_mode=True,
        with_state=True,
    )

    xpath = module.params["xpath"]
    element_xml = module.params["element"]
    edit = module.params["edit"]
    state = module.params["state"]

    try:
        existing_xml = module.connection.get(xpath)
        existing = xml.etree.ElementTree.fromstring(existing_xml).find("./result/")

        changed = False
        diff = {}

        if state == "present":
            if element_xml is None:
                module.fail_json(msg="'element' is required when state is 'present'.")

            if edit:
                element = xml.etree.ElementTree.fromstring(element_xml)

                # Edit action is a regular comparison between the two
                # XML documents for equality.
                if not xml_compare(existing, element):
                    changed = True

                    if not module.check_mode:  # pragma: no cover
                        module.connection.edit(xpath, element_xml)

            else:
                # When using set action, element can be an invalid XML document.
                # Wrap it in a dummy tag if so.
                try:
                    element = xml.etree.ElementTree.fromstring(element_xml)
                except xml.etree.ElementTree.ParseError:
                    element = xml.etree.ElementTree.fromstring(
                        "<wrapped>" + element_xml + "</wrapped>"
                    )

                if not xml_contained(existing, element):
                    changed = True

                    if not module.check_mode:  # pragma: no cover
                        module.connection.set(xpath, element_xml)

            diff = {
                "before": existing_xml,
                "after": element_xml,
            }

        # state == "absent"
        else:
            # Element exists, delete it.
            if existing is not None:
                changed = True

                if not module.check_mode:  # pragma: no cover
                    module.connection.delete(xpath)

                diff = {"before": existing_xml, "after": ""}

            # Element doesn't exist, nothing needs to be done.
            else:
                diff = {"before": "", "after": ""}

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:  # pragma: no cover
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":  # pragma: no cover
    main()
