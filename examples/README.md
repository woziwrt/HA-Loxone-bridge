# Examples

This directory contains opinionated, concrete examples of how to run the HAñLoxone bridge in real setups.

These examples are **not** generic and are meant as blueprints you can adapt.

## RB5009 humidifier example

See [`rb5009-humidifier/`](./rb5009-humidifier/) for:

- A sample `main.py` that talks to Home Assistant and Loxone.
- Example RouterOS `/container` configuration commands.
- A snapshot of firewall/NAT rules used in our setup.

> Note: RouterOS command syntax and available options may differ between firmware versions. Treat the commands as a starting point and adjust them to your RouterOS version.

## Releases

To create a user-facing release image for the bridge, always create a git tag first.  
Only tagged commits are built and published as versioned Docker images (e.g. `v0.1.0`).

```bash
 git tag v0.1.0 && git push origin v0.1.0
```
