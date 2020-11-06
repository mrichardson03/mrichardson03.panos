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
module: panos_tag_object
short_description: Create tag objects on PAN-OS devices.
description:
    - Create tag objects on PAN-OS devices.
author: "Michael Richardson (@mrichardson03)"
version_added: '1.0.0'
notes:
    - Panorama is supported.
    - Check mode is supported.
extends_documentation_fragment:
    - mrichardson03.panos.fragments.state
options:
    name:
        description:
            - Name of the tag.
        type: str
        required: true
    color:
        description:
            - Color for the tag.
        type: str
        choices:
            - red
            - green
            - blue
            - yellow
            - copper
            - orange
            - purple
            - gray
            - light green
            - cyan
            - light gray
            - blue gray
            - lime
            - black
            - gold
            - brown
    comments:
        description:
            - Comments for the tag.
        type: str
"""

EXAMPLES = """
- name: Create tag object 'Prod'
  panos_tag_object:
    name: 'Prod'
    color: 'red'
    comments: 'Prod Environment'

- name: Remove tag object 'Prod'
  panos_tag_object:
    name: 'Prod'
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

COLOR_NAMES = [
    "red",
    "green",
    "blue",
    "yellow",
    "copper",
    "orange",
    "purple",
    "gray",
    "light green",
    "cyan",
    "light gray",
    "blue gray",
    "lime",
    "black",
    "gold",
    "brown",
]


from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def color_code(color_name):
    """Return the color code for a color
    Args:
        color_name (str): One of the following colors:
                * red
                * green
                * blue
                * yellow
                * copper
                * orange
                * purple
                * gray
                * light green
                * cyan
                * light gray
                * blue gray
                * lime
                * black
                * gold
                * brown
    """
    colors = {
        "red": 1,
        "green": 2,
        "blue": 3,
        "yellow": 4,
        "copper": 5,
        "orange": 6,
        "purple": 7,
        "gray": 8,
        "light green": 9,
        "cyan": 10,
        "light gray": 11,
        "blue gray": 12,
        "lime": 13,
        "black": 14,
        "gold": 15,
        "brown": 16,
        "olive": 17,
        # there is no color18
        "maroon": 19,
        "red-orange": 20,
        "yellow-orange": 21,
        "forest green": 22,
        "turquoise blue": 23,
        "azure blue": 24,
        "cerulean blue": 25,
        "midnight blue": 26,
        "medium blue": 27,
        "cobalt blue": 28,
        "violet blue": 29,
        "blue violet": 30,
        "medium violet": 31,
        "medium rose": 32,
        "lavender": 33,
        "orchid": 34,
        "thistle": 35,
        "peach": 36,
        "salmon": 37,
        "magenta": 38,
        "red violet": 39,
        "mahogany": 40,
        "burnt sienna": 41,
        "chestnut": 42,
    }
    if color_name not in colors:
        raise ValueError("Color '{0}' is not valid".format(color_name))
    return "color" + str(colors[color_name])


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            color=dict(type="str", default=None, choices=COLOR_NAMES),
            comments=dict(type="str"),
        ),
        api_endpoint="/restapi/v10.0/Objects/Tags",
        with_state=True,
    )

    spec = {
        "entry": {"@name": module.params["name"], "comments": module.params["comments"]}
    }

    if module.params["color"]:
        spec["entry"]["color"] = color_code(module.params["color"])

    try:
        changed, diff = module.apply_state(spec)

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
