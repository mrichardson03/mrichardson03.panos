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
module: panos_import
short_description: Import files to a PAN-OS device.
description:
    - Import files to a PAN-OS device.
author:
    - Nathan Embery (@nembery)

version_added: '1.0.0'
requirements:
    - requests
options:
    category:
        description:
            - Category of file to import.
        type: str
        choices:
            - anti-virus
            - application-block-page
            - captive-portal-text
            - certificate
            - configuration
            - content
            - credential-block-page
            - credential-coach-text
            - custom-logo
            - data-filter-block-page
            - device-state
            - file-block-continue-page
            - file-block-page
            - global-protect-client
            - global-protect-clientless-vpn
            - global-protect-portal-custom-help-page
            - global-protect-portal-custom-home-page
            - global-protect-portal-custom-login-page
            - global-protect-portal-custom-welcome-page
            - high-availability-key
            - keypair
            - license
            - logdb
            - mfa-login-page
            - pandb-url-database
            - plugin
            - safe-search-block-page
            - saml-auth-internal-error-page
            - signed-url-database
            - software
            - ssl-cert-status-page
            - ssl-optout-text
            - url-block-page
            - url-coach-text
            - url-database
            - virus-block-page
            - wildfire
        default: software
    certificate_name:
        description:
            - When I(category=certificate), this is the name of the certificate object.
            - When I(category=keypair), the key pair will be associated with this certificate object.
        type: str
    format:
        description:
            - Format of the imported certifcate.
        type: str
        choices:
            - pem
            - pkcs12
    passphrase:
        description:
            - Passphrase used to decrypt the certificate and/or private key.
        type: str
    custom_logo_location:
        description:
            - When I(category=custom-logo), import this logo file here.
        type: str
        choices:
            - login-screen
            - main-ui
            - pdf-report-footer
            - pdf-report-header
    filename:
        description:
            - Location of the file to import into device.
        type: str
        aliases:
            - file
        required: false
"""

EXAMPLES = """
- name: Import software image into PAN-OS
  panos_import:
    category: software
    file: /tmp/PanOS_vm-10.0.1

- name: Import certificate
  panos_import:
    category: 'certificate'
    certificate_name: 'ISRG Root X1'
    format: 'pem'
    filename: '/tmp/isrgrootx1.pem'

- name: Import content
  panos_import:
    category: 'content'
    filename: '/tmp/panupv2-all-contents-8322-6317'

- name: Import named configuration snapshot
  panos_import:
    category: 'configuration'
    filename: '/tmp/config.xml'

- name: Import application block page
  panos_import:
    category: 'application-block-page'
    filename: '/tmp/application-block-page.html'

- name: Import custom logo
  panos_import:
    category: 'custom-logo'
    custom_logo_location: 'login-screen'
    filename: '/tmp/logo.jpg'
"""

RETURN = """
msg:
    description: A string with an error message, if any.
    returned: failure, always
    type: str
"""
