# Examples

This directory contains opinionated, concrete examples of how to run the HA–Loxone bridge in real setups.

These examples are **not** generic and are meant as blueprints you can adapt.

## RB5009 humidifier example

See [`rb5009-humidifier/`](./rb5009-humidifier/) for:

- A sample `main.py` that talks to Home Assistant and Loxone.
- Example RouterOS `/container` configuration commands.
- A snapshot of firewall/NAT rules used in our setup.

> Note: RouterOS command syntax and available options may differ between firmware versions. Treat the commands as a starting point and adjust them to your RouterOS version.
