# firewall

Ansible role that performs configuration of a PAN-OS firewall.

## Requirements

None.

## Role Variables

Available variables are listed below.

No variables are defined by default, and no configuration changes will be made
to the device unless defined by the calling playbook.  If variable is defined,
all existing elements of that type on the device will be **replaced** by the
defined configuration (for example, defining `interface_management_profiles`
will cause all existing interface management profiles to be overwritten).

The PAN-OS configuration will be committed if changes are made by this role.

### Interface Management Profiles

```
interface_management_profiles:
  - name: Ping
    ping: True
```

List of dictionaries specifying interface management profiles.  The following
keys can be specified for each profile:

- `name`: Name of the management profile (string).
- `http`: Enable HTTP (boolean).
- `http_oscp`: Enable HTTP OSCP (boolean).
- `https`: Enable HTTPS (boolean).
- `ping`: Enable ping (boolean).
- `response_pages`: Enable response pages (boolean).
- `snmp`: Enable SNMP (boolean).
- `ssh`: Enable SSH (boolean).
- `telnet`: Enable telnet (boolean).
- `userid_service`: Enable User-ID agent (boolean).
- `userid_syslog_listener_ssl`: Enable User-ID syslog listener over SSL (boolean).
- `userid_syslog_listener_udp`: Enable User-ID syslog listener over UDP (boolean).
- `permitted_ip`: Permitted IPv4 and IPv6 IP addresses (list of strings).

### Ethernet Interfaces

```
ethernet_interfaces:
  - name: 'ethernet1/1'
    dhcp: True
    interface_management_profile: 'Ping'
```

List of dictonaries specifying ethernet interfaces.  The following keys can be
specified for each ethernet interface:

- `name`: Name of the ethernet interface (string).
- `dhcp`: Use DHCP for interface address (boolean).
- `dhcp_create_default_route`: Allow DHCP to create a default route on this
  interface (boolean).
- `interface_management_profile`: Management profile for this interface (string).

### Virtual Routers

```
virtual_routers:
  - name: 'default'
    interfaces:
      - 'ethernet1/1'
      - 'ethernet1/2'
```

List of dictionaries specifying virtual routers.  The following keys can be
specified for each virtual router:

- `name`: Name of the virtual router (string).
- `interfaces`: Interfaces included in this virtual router (list of strings).

### Zones

```
zones:
  - name: 'untrust'
    interfaces:
      - 'ethernet1/1'
```

List of dictionaries specifying zones.  The following keys can be specified for
each zone:

- `name`: Name of the zone (string).
- `type`: Zone type (string, default: `layer3`).
- `interfaces`: Interfaces included in this zone (list of strings).

### Address Objects

```
address_objects:
  - name: 'ubuntu-int'
    value: '10.0.1.20'
```

List of dictionaries specifying address objects.  The following keys can be
specified for each address object:

- `name`: Name of address object (string).
- `type`: Address object type (string, default: `ip-netmask`).
- `description`: Description of address object (string).
- `tags`: Tags assigned to this address object (list of strings).

### Service Objects

```
service_objects:
  - name: 'ssh-tcp-22'
    protocol: 'tcp'
    destination_port: '22'
```

List of dictionaries specifying service objects.  The following keys can be
specified for each service object:

- `name`: Name of service object (string).
- `protocol`: Service object protocol (string).
- `description`: Description of service object (string).
- `tags`: Tags assigned to this service object (list of strings).

### Security Profile Groups

```
security_profile_groups:
  - name: Outbound
    antivirus: strict
    spyware: strict
    vulnerability: strict
    url: default
    file_blocking: 'strict file blocking'
    wildfire: default
```

List of dictionaries specifying security profile groups.  The following keys
can be specified for each security profile group:

- `name`: Name of security profile group (string).
- `virus`: Anti-virus profile (string).
- `spyware`: Anti-spyware profile (string).
- `vulnerability`: Vulnerabilty protection profile (string).
- `url`: URL filtering profile (string).
- `file_blocking`: File blocking profile (string).
- `wildfire`: WildFire analysis profile (string).

### Security Rules

```
security_rules:
  - name: 'Allow SSH'
    source_zone:
      - 'untrust'
    destination_zone:
      - 'trust'
    destination_ip:
      - '10.0.0.10'
    applications:
      - 'ssh'
```

List of dictionaries specifying security rules.  The following keys can be
specified for each security rule:

- `name`: Name of security rule (string).
- `description`: Description of security rule (string).
- `source_zone`: Source zones (list of strings).
- `source_ip`: Source IP addresses (list of strings, default: `['any']`).
- `source_user`: Source users.
- `destination_zone`: Destination zones (list of strings).
- `destination_ip`: Destination IP addresses (list of strings, default: `['any']`).
- `category`: URL categories (list of strings, default: `['any']`).
- `application`: Applications (list of strings, default: `['any']`).
- `service`: Services (list of strings, default: `['application-default']`).
- `security_profile_group`: Security profile group (string).  Mutually exclusive
  with `security_profiles`.
- `security_profiles`: Security profiles for rule (dictionary).  Mutually
  exclusive with `security_profile_group`.  Keys:
    - `virus`: Anti-virus profile (string).
    - `spyware`: Anti-spyware profile (string).
    - `vulnerability`: Vulnerabilty protection profile (string).
    - `url`: URL filtering profile (string).
    - `file_blocking`: File blocking profile (string).
    - `wildfire`: WildFire analysis profile (string).
- `action`: Action to take on traffic (string, default: `allow`).
- `disabled`: Rule is disabled (boolean).
- `tags`: Tags assigned to this rule (list of strings).
- `group_tag`: Group rules by this tag (string).

### NAT Rules

```
nat_rules:
  - name: 'Inbound SSH'
    source_zone:
      - 'untrust'
    destination_zone: 'untrust'
    destination_ip:
      - '10.0.0.10'
    service: 'ssh-tcp-22'
    source_translation: True
    source_translation_type: 'dynamic-ip-and-port'
    source_translation_interface: 'ethernet1/2'
    destination_translation: True
    destination_translated_port: '22'
    destination_translated_address: 'ubuntu-int'
```

List of dictionaries specifying NAT rules.  The following keys can be specified
for each NAT rule:

- `name`: Name of NAT rule (string).
- `source_zone`: Original packet source zones (list of strings).
- `source_ip`: Original packet source IP addresses (list of strings,
  default: `['any']`).
- `destination_zone`: Original packet destination zone (string).
- `destination_ip`: Original packet destination IP addresses (list of strings,
  default: `['any']`).
- `service`: Original packet service (list).
- `source_translation`: Perform source translation (boolean).
- `source_translation_type`: Source translation type (string,
  values: `dynamic-ip-and-port`).
- `source_translation_interface`: Source translation interface when
  `source_translation_type` is `dynamic-ip-and-port` (string).
- `destination_translation`: Perform destination translation (boolean).
- `destination_translated_address`: Translated destination address (string).
- `destination_translated_port`: Translated destination port (string).

Dependencies
------------

None.

Example Playbook
----------------

```
---
- hosts: fw

  collections:
    - mrichardson03.panos

  vars:
    interface_management_profiles:
      - name: Ping
        ping: True

    ethernet_interfaces:
      - name: 'ethernet1/1'
        dhcp: True
        interface_management_profile: 'Ping'
      - name: 'ethernet1/2'
        dhcp: True
        dhcp_create_default_route: False
        interface_management_profile: 'Ping'

    virtual_routers:
      - name: 'default'
        interfaces:
          - 'ethernet1/1'
          - 'ethernet1/2'

    zones:
      - name: 'untrust'
        interfaces:
          - 'ethernet1/1'
      - name: 'trust'
        interfaces:
          - 'ethernet1/2'

    address_objects:
      - name: 'ubuntu-int'
        value: '10.0.1.20'

    service_objects:
      - name: 'ssh-tcp-22'
        protocol: 'tcp'
        destination_port: '22'

    security_profile_groups:
      - name: Inbound
        vulnerability: strict
      - name: Outbound
        antivirus: strict
        spyware: strict
        vulnerability: strict
        url: default
        file_blocking: 'strict file blocking'
        wildfire: default

    security_rules:
      - name: 'Allow SSH'
        source_zone:
          - 'untrust'
        destination_zone:
          - 'trust'
        destination_ip:
          - '10.0.0.10'
        applications:
          - 'ssh'
  
      - name: 'Allow Outbound'
        source_zone:
          - 'trust'
        destination_zone:
          - 'untrust'
        security_profile_group: 'Outbound'

    nat_rules:
      - name: 'Inbound SSH'
        source_zone:
          - 'untrust'
        destination_zone: 'untrust'
        destination_ip:
          - '10.0.0.10'
        service: 'ssh-tcp-22'
        source_translation: True
        source_translation_type: 'dynamic-ip-and-port'
        source_translation_interface: 'ethernet1/2'
        destination_translation: True
        destination_translated_port: '22'
        destination_translated_address: 'ubuntu-int'

      - name: 'Outbound'
        source_zone:
          - 'trust'
        destination_zone: 'untrust'
        source_translation: True
        source_translation_type: 'dynamic-ip-and-port'
        source_translation_interface: 'ethernet1/1'

  roles:
    - firewall
```

License
-------

ISC

Author Information
------------------

- Michael Richardson (@mrichardson03)
