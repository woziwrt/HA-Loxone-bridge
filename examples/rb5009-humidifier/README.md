# RB5009 humidifier example

This example shows how we run the HAñLoxone bridge for a single humidifier on a MikroTik RB5009 using RouterOS containers.

It is not a drop-in configuration. You are expected to adapt entity IDs, IP addresses and RouterOS commands to your own setup.

> RouterOS notice: The `/container` commands shown here are illustrative. Command syntax and available options may differ between RouterOS versions, so you may need to adapt them to your system.

## Overview

- Home Assistant runs in a container, reachable as `http://homeassistant:8123`.
- The HAñLoxone bridge runs in a separate container and mounts `main.py` from the host.
- `main.py` reads humidifier state from Home Assistant and can push data or commands to Loxone via virtual inputs/outputs.

## Example main.py

See [`main.py`](./main.py) for a minimal bridge stub:

- Reads `HA_URL` and `HA_TOKEN` from environment variables.
- Fetches the state of one Home Assistant entity (humidifier).
- Prints the state to stdout and exits.

You can copy this file and extend it with your own logic:
mapping between Home Assistant entities and Loxone virtual inputs/outputs.

## Example RouterOS container commands

Note: The following RouterOS /container commands are illustrative. Some details (flags,
parameters) can differ between RouterOS versions. Adjust them to match your firmware.

The following commands show how you might configure the containers on RB5009.

Adjust:

- `10.33.1.222` to your RB5009 address.
- Paths under `/usb1/ha-loxone-bridge-runtime` to wherever you unpacked the tarball.
- `HA_URL`, `HA_TOKEN`, `LOXONE_*` to your real values.

## Create a container network

```bash
 /container/config/set registry-url="" max-concurrent-downloads=2
 /container/veth/add name=veth-ha address=172.18.0.2/24 gateway=172.18.0.1
 /container/veth/add name=veth-bridge address=172.18.0.3/24 gateway=172.18.0.1
 /interface/bridge/add name=br-containers
 /interface/bridge/port/add bridge=br-containers interface=veth-ha
 /interface/bridge/port/add bridge=br-containers interface=veth-bridge
``` 
## Home Assistant container (example)

## Assumes you already have a Home Assistant image imported

```bash
 /container/add name=homeassistant \
  interface=veth-ha \ 
  root-dir=/usb1/homeassistant \
  envlist=homeassistant-env \
  start-on-boot=yes
```
## HA Loxone bridge container

```bash
 /container/add name=ha-loxone-bridge \
  interface=veth-bridge \
  root-dir=/usb1/ha-loxone-bridge-runtime \
 envlist=ha-loxone-bridge-env \
 start-on-boot=yes
```

## Environment for the bridge

```bash
 /container/envs/add name=ha-loxone-bridge-env key=HA_URL value="http://homeassistant:8123"
 /container/envs/add name=ha-loxone-bridge-env key=HA_TOKEN value="YOUR_LONG_LIVED_TOKEN"
 /container/envs/add name=ha-loxone-bridge-env key=LOXONE_HOST value="loxone.local"
 /container/envs/add name=ha-loxone-bridge-env key=LOXONE_USER value="loxone_user"
 /container/envs/add name=ha-loxone-bridge-env key=LOXONE_PASSWORD value="loxone_password"
```

## Start containers

```bash
 /container/start homeassistant
 /container/start ha-loxone-bridge
```

Again, treat this as a rough template; you will likely need to tweak flags and paths.

## Firewall / NAT snapshot

The file [`firewall-nat.txt`](./firewall-nat.txt) contains an example of the NAT rules we used when testing this bridge. It is included as documentation only and is not a recommended default firewall configuration.





