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
module: panos_facts
short_description: Collects facts from PAN-OS devices
description:
    - Collects fact information from Palo Alto Networks firewalls and Panorama.
author:
    - Michael Richardson (@mrichardson03)
notes:
    - Panorama is supported.
    - Check mode is not supported.
version_added: '1.0.0'
"""

EXAMPLES = """
- name: Gather system facts
  panos_facts:
"""

RETURN = """
ansible_net_hostname:
    description: Hostname of the local node.
    returned: always
    type: str
ansible_net_serialnum:
    description: Serial number of the local node.
    returned: always
    type: str
ansible_net_model:
    description: Device model of the local node.
    returned: always
    type: str
ansible_net_version:
    description: PanOS version of the local node.
    returned: always
    type: str
ansible_net_uptime:
    description: Uptime of the local node.
    returned: always
    type: str
    sample: 469 days, 19:30:16
ansible_net_vm_uuid:
    description: UUID of the local node.
    returned: When the device model is "PA-VM"
    type: str
ansible_net_vm_cpuid:
    description: CPU ID of the local node.
    returned: When the device model is "PA-VM"
    type: str
ansible_net_vm_license:
    description: PA-VM License of the local node.
    returned: When the device model is "PA-VM"
    type: str
ansible_net_vm_cap_tier:
    description: VM Capacity Tier of the local node.
    returned: When the device model is "PA-VM"
    type: str
ansible_net_vm_cpu_count:
    description: Number of vCPU Cores of the local node.
    returned: When the device model is "PA-VM"
    type: str
ansible_net_vm_memory:
    description: Memory (in bytes) of the local node.
    returned: When the device model is "PA-VM"
    type: str
ansible_net_vm_mode:
    description: VM Mode of the local node.
    returned: When the device model is "PA-VM"
    type: str
ansible_net_full_commit_required:
    description: Specifies whether full commit is required to apply changes.
    returned: always
    type: bool
ansible_net_uncommitted_changes:
    description: Specifies if commit is required to apply changes.
    returned: always
    type: bool
ansible_net_multivsys:
    description: Specifies whether multivsys mode is enabled on local node.
    returned: always
    type: str
    sample: on
ansible_net_ha_enabled:
    description: Specifies if HA is enabled.
    returned: always
    type: bool
ansible_net_ha_localmode:
    description: Specifies the HA mode on local node.
    returned: When C(ha) is enabled.
    type: str
    sample: Active-Passive
ansible_net_ha_localstate:
    description: Specifies the HA state on local node.
    returned: When C(ha) is enabled.
    type: str
    sample: active
ansible_net_interfaces:
    description: Network interface information.
    returned: always
    type: complex
    contains:
        name:
            description: Interface name.
            type: str
            sample: ae1.23
        comment:
            description: Interface description/comment.
            type: str
        ip:
            description: List of interface IP addresses in CIDR format.
            type: list
            sample: 192.0.2.1/24
        ipv6:
            description: List of interface IPv6 addresses in CIDR format.
            type: list
            sample: 2001:db8::0000:1/64
        tag:
            description: VLAN tag for the subinterface.
            type: int
            sample: 23
        vsys:
            description: Virtual system interface is assigned to.
            type: str
            sample: vsys1
        zone:
            description: Zone assigned to interface.
            type: str
            sample: untrust
"""

import xml.etree.ElementTree as ET

from ansible.module_utils.connection import ConnectionError
from ansible_collections.mrichardson03.panos.plugins.module_utils.panos import (
    PanOSAnsibleModule,
)


def system_facts(conn):
    facts = dict()

    # Standard system info
    system_info_xml = conn.op("show system info", is_xml=False)
    system_info = ET.fromstring(system_info_xml).find("./result/system")

    facts.update(
        {
            "ansible_net_hostname": system_info.findtext("hostname"),
            "ansible_net_model": system_info.findtext("model"),
            "ansible_net_serialnum": system_info.findtext("serial"),
            "ansible_net_version": system_info.findtext("sw-version"),
            "ansible_net_uptime": system_info.findtext("uptime"),
            "ansible_net_multivsys": system_info.findtext("multi-vsys"),
        }
    )

    # grab VM-Series specific information if available
    if facts["ansible_net_model"] == "PA-VM":
        facts.update(
            {
                "ansible_net_vm_uuid": system_info.findtext("vm-uuid"),
                "ansible_net_vm_cpuid": system_info.findtext("vm-cpuid"),
                "ansible_net_vm_license": system_info.findtext("vm-license"),
                "ansible_net_vm_cap_tier": system_info.findtext("vm-cap-tier"),
                "ansible_net_vm_cpu_count": system_info.findtext("vm-cpu-count"),
                "ansible_net_vm_memory": system_info.findtext("vm-memory"),
                "ansible_net_vm_mode": system_info.findtext("vm-mode"),
            }
        )
    # Check uncommitted changes
    pending_changes_xml = conn.op("check pending-changes", is_xml=False)
    pending_changes = ET.fromstring(pending_changes_xml).findtext("./result")

    if pending_changes == "yes":
        uncommitted_changes = True
    else:
        uncommitted_changes = False

    # Check if full commit is required
    if uncommitted_changes:
        full_commit_xml = conn.op("check full-commit-required", is_xml=False)
        full_commit = ET.fromstring(full_commit_xml).findtext("./result")

        if full_commit == "yes":
            full_commit_required = True
        else:
            full_commit_required = False
    else:
        full_commit_required = False

    facts.update(
        {
            "ansible_net_uncommitted_changes": uncommitted_changes,
            "ansible_net_full_commit_required": full_commit_required,
        }
    )

    return facts


def ha_facts(conn):
    facts = dict()

    show_ha_xml = conn.op("show high-availability all", is_xml=False)
    show_ha = ET.fromstring(show_ha_xml).find("./result")

    if show_ha.findtext("./enabled") == "yes":
        ha_enabled = True

        if conn.is_panorama() is False:
            ha_localmode = show_ha.findtext("./group/local-info/mode")
            ha_localstate = show_ha.findtext("./group/local-info/state")
        else:
            ha_localmode = "Active-Passive"
            ha_locastate = show_ha.findtext("./local-info/state")

    else:
        ha_enabled = False

    facts.update(
        {
            "ansible_net_ha_enabled": ha_enabled,
        }
    )

    if ha_enabled:
        facts.update(
            {
                "ansible_net_ha_localmode": ha_localmode,
                "ansible_net_ha_locastate": ha_localstate,
            }
        )

    return facts


def interface_facts(conn):
    facts = dict()
    interfaces = list()

    show_interface_xml = conn.op('show interface "all"', is_xml=False)
    show_interface = ET.fromstring(show_interface_xml).find("./result")

    get_interface_xml = conn.get(
        xpath="/config/devices/entry[@name='localhost.localdomain']/network/interface"
    )
    get_interface = ET.fromstring(get_interface_xml).find("./result")

    for interface in show_interface.findall("./ifnet/entry"):
        iface = dict()

        iface["name"] = interface.findtext("name")
        iface["zone"] = interface.findtext("zone")
        iface["ip"] = interface.findtext("ip")
        iface["ipv6"] = interface.findtext("addr6")
        iface["vsys"] = "vsys" + interface.findtext("vsys")
        iface["tag"] = interface.findtext("tag")

        if "ethernet" in iface["name"]:
            iface["comment"] = get_interface.findtext(
                "./interface/ethernet/entry[@name='{0}']/comment".format(iface["name"])
            )
        elif "tunnel" in iface["name"]:
            iface["comment"] = get_interface.findtext(
                "./interface/tunnel/units/entry[@name='{0}']/comment".format(
                    iface["name"]
                )
            )

        interfaces.append(iface)

    facts["ansible_net_interfaces"] = interfaces

    return facts


def main():
    module = PanOSAnsibleModule(
        argument_spec=dict(),
        supports_check_mode=False,
    )

    ansible_facts = dict()

    try:
        pass
        ansible_facts.update(system_facts(module.connection))
        ansible_facts.update(ha_facts(module.connection))

        if module.connection.is_panorama() is False:
            ansible_facts.update(interface_facts(module.connection))

    except ConnectionError as e:
        module.fail_json(msg="{0}".format(e))

    module.exit_json(ansible_facts=ansible_facts)


if __name__ == "__main__":
    main()
