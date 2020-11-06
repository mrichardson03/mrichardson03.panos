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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: panos_schedule_object
short_description: Create schedule objects on PAN-OS devices.
description:
    - Create schedule objects on PAN-OS devices.
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
            - Name of the object.
        type: str
        required: true
    disable_override:
        description:
            - If the override is disabled
        type: bool
    type:
        description:
            - Type of schedule
        type: str
        choices:
            - recurring
            - non-recurring
    non_recurring_date_time:
        description:
            - Date and time range string (e.x. '2019/11/01@00:15-2019/11/28@00:30') for a non-recurring schedule
        type: list
        elements: str
    recurrence:
        description:
            - Recurrence schedule
        type: str
        choices:
            - daily
            - weekly
    daily_time:
        description:
            - Time range (e.x. '17:00-19:00') for a daily recurring schedule
        type: list
        elements: str
    weekly_sunday_time:
        description:
            - Time range (e.x. '17:00-19:00') for a weekly recurring schedule (Sunday)
        type: list
        elements: str
    weekly_monday_time:
        description:
            - Time range (e.x. '17:00-19:00') for a weekly recurring schedule (Monday)
        type: list
        elements: str
    weekly_tuesday_time:
        description:
            - Time range (e.x. '17:00-19:00') for a weekly recurring schedule (Tuesday)
        type: list
        elements: str
    weekly_wednesday_time:
        description:
            - Time range (e.x. '17:00-19:00') for a weekly recurring schedule (Wednesday)
        type: list
        elements: str
    weekly_thursday_time:
        description:
            - Time range (e.x. '17:00-19:00') for a weekly recurring schedule (Thursday)
        type: list
        elements: str
    weekly_friday_time:
        description:
            - Time range (e.x. '17:00-19:00') for a weekly recurring schedule (Friday)
        type: list
        elements: str
    weekly_saturday_time:
        description:
            - Time range (e.x. '17:00-19:00') for a weekly recurring schedule (Saturday)
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create schedule object
  panos_schedule_object:
    name: 'Monday-Work-Day'
    type: 'recurring'
    recurrence: 'weekly'
    weekly_monday_time:
      - '09:00-17:00'

- name: Create non-recurring schedule object
  panos_schedule_object:
    name: 'Week-of-Sept-21'
    type: 'non-recurring'
    non_recurring_date_time: '2020/09/21@00:15-2020/09/25@17:00'
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

from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            disable_override=dict(type="bool"),
            type=dict(type="str", choices=["recurring", "non-recurring"]),
            non_recurring_date_time=dict(type="list", elements="str"),
            recurrence=dict(type="str", choices=["daily", "weekly"]),
            daily_time=dict(type="list", elements="str"),
            weekly_sunday_time=dict(type="list", elements="str"),
            weekly_monday_time=dict(type="list", elements="str"),
            weekly_tuesday_time=dict(type="list", elements="str"),
            weekly_wednesday_time=dict(type="list", elements="str"),
            weekly_thursday_time=dict(type="list", elements="str"),
            weekly_friday_time=dict(type="list", elements="str"),
            weekly_saturday_time=dict(type="list", elements="str"),
        ),
        mutually_exclusive=[
            ["non_recurring_date_time", "recurrence"],
            ["daily_time", "weekly_sunday_time"],
            ["daily_time", "weekly_monday_time"],
            ["daily_time", "weekly_tuesday_time"],
            ["daily_time", "weekly_wednesday_time"],
            ["daily_time", "weekly_thursday_time"],
            ["daily_time", "weekly_friday_time"],
            ["daily_time", "weekly_saturday_time"],
        ],
        api_endpoint="/restapi/v10.0/Objects/Schedules",
        with_state=True,
    )

    spec = {
        "entry": {
            "@name": module.params["name"],
            "schedule-type": {module.params["type"]: {}},
        }
    }

    if module.params["type"] == "non-recurring":
        spec["entry"]["schedule-type"]["non-recurring"] = {
            "member": module.params["non_recurring_date_time"]
        }

    else:
        recurrence = {}

        if module.params["recurrence"] == "daily" and module.params["daily_time"]:
            recurrence.update({"daily": {"member": module.params["daily_time"]}})

            spec["entry"]["schedule-type"]["recurring"] = recurrence

        else:
            recurrence = {"weekly": {}}

            if module.params["weekly_sunday_time"]:
                recurrence["weekly"].update(
                    {"sunday": {"member": module.params["weekly_sunday_time"]}}
                )

            if module.params["weekly_monday_time"]:
                recurrence["weekly"].update(
                    {"monday": {"member": module.params["weekly_monday_time"]}}
                )

            if module.params["weekly_tuesday_time"]:
                recurrence["weekly"].update(
                    {"tuesday": {"member": module.params["weekly_tuesday_time"]}}
                )

            if module.params["weekly_wednesday_time"]:
                recurrence["weekly"].update(
                    {"wednesday": {"member": module.params["weekly_wednesday_time"]}}
                )

            if module.params["weekly_thursday_time"]:
                recurrence["weekly"].update(
                    {"thursday": {"member": module.params["weekly_thursday_time"]}}
                )

            if module.params["weekly_friday_time"]:
                recurrence["weekly"].update(
                    {"friday": {"member": module.params["weekly_friday_time"]}}
                )

            if module.params["weekly_saturday_time"]:
                recurrence["weekly"].update(
                    {"saturday": {"member": module.params["weekly_saturday_time"]}}
                )

            spec["entry"]["schedule-type"]["recurring"] = recurrence

    try:
        changed, diff = module.apply_state(spec)

        module.exit_json(changed=changed, diff=diff)

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))


if __name__ == "__main__":
    main()
