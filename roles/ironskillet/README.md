# ironskillet

An Ansible Role that installs a set of best practices configuration to a
Palo Alto Networks NGFW.

Supports PAN-OS 10.0.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values
(see `defaults/main.yml`):

```
fw_name: '{{ inventory_hostname }}'
```

Sets the name of the firewall. Default is to use the hostname as defined in
the Ansible inventory.

```
configure_dns: False
dns_primary: 8.8.8.8
dns_secondary: 8.8.4.4
```

DNS configuration options. DNS servers are only modified to these values if
`configure_dns` is set to `True`.

```
ntp_primary: 0.pool.ntp.org
ntp_secondary: 1.pool.ntp.org
```

NTP configuration options.

```
sinkhole_ipv4: sinkhole.paloaltonetworks.com
sinkhole_ipv6: 2600:5200::1
```

Servers to use for the [DNS Sinkhole](https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-admin/threat-prevention/use-dns-queries-to-identify-infected-hosts-on-the-network/dns-sinkholing.html)
functionality in the created Anti-Spyware profile.

```
email_profile_gateway: 192.0.2.1
email_profile_from: sentfrom@yourdomain.com
email_profile_to: sendto@yourdomain.com
```

Default values for the created email logging profile.

```
syslog_server: 192.0.2.2
```

Default values for the created syslog profile.

```
api_key_lifetime: 525600
```

Configured API key lifetime.

```
include_panw_edl: False
```

Create security rules referencing the built-in External Dynamic Lists
**panw-highrisk-ip-list**, **panw-known-ip-list**, **panw-bulletproof-ip-list**.

## Dependencies

None.

## Example Playbook

    - hosts: firewalls

      roles:
         - mrichardson03.panos.ironskillet

## License

ISC

## Authors

- Scott Shoaf (@scotchoaf)
- Bob Hagen (@stealthllama)
- Nate Embery (@nembery)
- Michael Richardson (@mrichardson03)
