# SZTPD

SZTPD is in implementation of the "bootstrap server" defined in [RFC 8572](https://www.rfc-editor.org/rfc/rfc8572.html): 
Secure Zero Touch Provisioning (SZTP).

## Installation

  `pip install sztpd`

  Some system-level packages may need to be installed.

## Overview

  - implemented on top of the [YANGcore](https://pypi.org/project/yangore/) application server.
  - Bootstrapping log per device
  - Plugin-based dynamic callouts to relay progress reports
  - Plugin-based dynamic callouts for ownership verification
  - Plugin-based dynamic callouts for response manager
  - Support for [RFC 9646](https://www.rfc-editor.org/rfc/rfc9646.html): Conveying a Certificate
    Signing Request (CSR) in a Secure Zero-Touch Provisioning (SZTP) Bootstrapping Request

## Motivation

Secure zero touch bootstrapping is important to scale deployments.  Pure Python
apps are highly portable and easy to install.  A simple to install solution
helps adoptability and hence more use, and the world is a safer.

## More Information

Please see the [documentation](https://watsen.net/docs) for more information.

