# PAN-OS Ansible Collection - paloaltonetworks.panos_enhanced

![CI/CD](https://github.com/PaloAltoNetworks/panos_enhanced/workflows/CI/CD/badge.svg)

Ansible collection for automating configuration and operational tasks on
Palo Alto Networks Next Generation Firewalls using the PAN-OS API.

For more documentation, check the [project wiki](https://github.com/PaloAltoNetworks/panos_enhanced/wiki).

## How is this different than paloaltonetworks.panos?

This collection is different than the official Palo Alto Networks collection in
a number of key ways:

- **Direct XML API support.** All aspects of PAN-OS can be configured using the
  standard Ansible Jinja2 templating language.
- **Designed for customization.** Action plugins can further extend the modules
  in this collection to support complex workflows.
- **Uses standard Ansible connection methods.** This collection is written using
  as an Ansible `httpapi` plugin. This allows for a number of enhancements,
  most notably persistent connections to the device.
- **No more non-standard dependencies.** Only Python modules shipped in
  Ansible Tower are used, `xmltodict` and `requests`.

This collection is **not backwards compatible** with `paloaltonetworks.panos`.

## Included Roles

Ansible roles for common tasks are also included:

- [onboard](https://github.com/PaloAltoNetworks/panos_enhanced/tree/develop/roles/onboard):
  Performs common initial configuration steps: licensing, install latest content,
  upgrade to a new PAN-OS version.
- [ironskillet](https://github.com/PaloAltoNetworks/panos_enhanced/tree/develop/roles/ironskillet):
  Installs a best practices initial configuration.

## Installation

Install this collection using the Ansible Galaxy CLI:

```
ansible-galaxy collection install paloaltonetworks.panos_enhanced
```

## Usage

### Sample Playbook

```yaml
---
- hosts: firewall

  collections:
    - paloaltonetworks.panos_enhanced

  vars:
    address_objects:
      - name: "web-srv"
        value: "192.168.45.5"
      - name: "db-srv"
        value: "192.168.35.5"
        type: "ip-netmask"
        description: "database server"
      - name: "fqdn-test"
        type: "fqdn"
        value: "foo.bar.baz"

  tasks:
    - name: Create any configuration you want!
      panos_config_element:
        xpath: "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/profiles/vulnerability"
        element: |
          <entry name="Outbound-Vuln-Profile">
            <rules>
              <entry name="Block-Critical-High-Medium">
                <action>
                  <reset-both/>
                </action>
                <vendor-id>
                  <member>any</member>
                </vendor-id>
                <severity>
                  <member>critical</member>
                  <member>high</member>
                  <member>medium</member>
                </severity>
                <cve>
                  <member>any</member>
                </cve>
                <threat-name>any</threat-name>
                <host>any</host>
                <category>any</category>
                <packet-capture>single-packet</packet-capture>
              </entry>
            </rules>
          </entry>

    - name: Create multiple objects at once, and use Jinja!
      panos_config_element:
        xpath: "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address"
        element: |
          {% for object in address_objects %}
            <entry name="{{ object.name }}">
              <{{ object.type | default("ip-netmask") }}>{{ object.value }}</{{ object.type | default("ip-netmask") }}>
          {% if 'description' in object %}
              <description>{{ object.description }}</description>
          {% endif %}
            </entry>
          {% endfor %}
```

### Customization through Action Plugins

Don't care for XML in your playbooks? Use an
[action plugin](https://github.com/PaloAltoNetworks/panos_enhanced/blob/develop/plugins/action/panos_address_object.py)
to turn this:

```yaml
- name: Create address object
  panos_config_element:
    xpath: "/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='vsys1']/address"
    element: |
      <entry name="web-srv">
        <ip-netmask>192.168.45.5</ip-netmask>
      </entry>
```

into this:

```yaml
- name: Create address object
  panos_address_object:
    name: "web-srv"
    value: "192.168.45.5"
```

### Sample Inventory

Configuration options can be specified using host variables, like the following:

```
fw        ansible_host=192.168.55.10

[all:vars]
ansible_user=admin
ansible_password=P4loalto!

ansible_network_os=paloaltonetworks.panos_enhanced.panos
ansible_connection=httpapi
ansible_httpapi_use_ssl=True
ansible_httpapi_validate_certs=False
```

See the [httpapi connection documentation](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/httpapi_connection.html) for the full list of options.

Authentication via API key is also supported using the variable
`ansible_api_key`.

## Python Compatability

This collection is written for Python 3.6.8, which is the version used in the
default Ansible Tower/AWX virtual environment. Newer versions of Python will
likely work, but are not tested.

## Support

This template/solution is released under an as-is, best effort, support
policy. These scripts should be seen as community supported and Palo
Alto Networks will contribute our expertise as and when possible. We do
not provide technical support or help in using or troubleshooting the
components of the project through our normal support options such as
Palo Alto Networks support teams, or ASC (Authorized Support Centers)
partners and backline support options. The underlying product used (the
VM-Series firewall) by the scripts or templates are still supported, but
the support is only for the product functionality and not for help in
deploying or using the template or script itself.

Unless explicitly tagged, all projects or work posted in our GitHub
repository (at <https://github.com/PaloAltoNetworks>) or sites other
than our official Downloads page on <https://support.paloaltonetworks.com>
are provided under the best effort policy.
