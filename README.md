# HA–Loxone Bridge (RB5009 example)

This repository documents how we run a custom bridge between Loxone and Home Assistant inside containers on a MikroTik RB5009.  
It is not a universal “works with everything” solution, but a concrete, working example you can adapt for your own setup.

## What this project is (and is not)

- It provides:
  - A Docker runtime image (Python + required libraries) that can run a user-provided `main.py` bridge script.
  - An example setup tested on MikroTik RB5009, where both Home Assistant and this bridge run in containers.
  - Example bridge logic for one specific device (humidifier) as a reference for your own scripts.

- It does **not** provide:
  - A generic bridge that automatically knows how to handle all Home Assistant devices and entities.
  - A ready-made configuration for every platform (MikroTik, Raspberry Pi, NAS, …).
  - A tutorial on how to program in Python or how to configure Home Assistant in general.

In other words: this repo shows our working solution and gives you the tools and patterns to build your own.

## Prerequisites

- A running Home Assistant instance reachable from the bridge container.
- A Loxone Miniserver with access to create virtual inputs/outputs.
- Basic familiarity with Docker or MikroTik RouterOS container configuration.

## High-level architecture

- Home Assistant runs in a container, reachable at `http://homeassistant:8123` (or similar), using the standard port 8123.  
- The bridge runs in a separate container and talks to:
  - Home Assistant (HTTP/WebSocket API, long-lived token).
  - Loxone (using its API/protocol via a Python library or direct requests).

The bridge logic is implemented in a Python script `main.py`, which is **not** hard-coded into the image.  
Instead, the Docker image provides a runtime environment and expects you to mount your own `main.py` from the host.

## RB5009 example: how we run it

This project was originally designed and tested on a MikroTik RB5009, using RouterOS container functionality.

Conceptually, the equivalent of `docker run` looks like this (simplified):

```bash
docker run -d 
   --name ha-loxone-bridge 
   -v /path/on/host/main.py:/app/main.py:ro 
   -e HA_URL=http://homeassistant:8123 
   -e HA_TOKEN=YOUR_LONG_LIVED_TOKEN 
   -e LOXONE_HOST=loxone.local
   -e LOXONE_USER=loxone_user
   -e LOXONE_PASSWORD=loxone_password
  ghcr.io/woziwrt/ha-loxone-bridge:runtime
``` 


On RB5009 this is configured via the RouterOS `/container` settings (environment, mounts, image), but the idea is the same:  
use one stable runtime image, and keep your `main.py` and credentials on the host.

> In the `examples/` folder you will find a concrete example configuration for RB5009 and a sample `main.py` for a humidifier once it is added.

## Example bridge script (`main.py`)

Because every Home Assistant setup is different (different devices, entity IDs, automations), the bridge script is always specific to your installation.

This repository will contain:

- A sample `main.py` for one real device (for example, a humidifier) that:
  - Connects to Home Assistant using `HA_URL` and `HA_TOKEN`.
  - Talks to Loxone using `LOXONE_*` settings.
  - Maps a small set of Home Assistant entities to Loxone actions.

You are expected to:

- Copy this sample script as a starting point.
- Adjust entity IDs, logic and behaviour to match your own devices.
- Keep your modified `main.py` outside of the image and mount it into the container.

We intentionally do **not** try to cover all possible devices or HA configurations in code.

## How to use this repository

There are two main ways to use this project:

### 1. Use the runtime image + your own `main.py` (recommended)

This is the closest to how we run it on RB5009.

- Build or pull the runtime image (multi-arch build and releases will be provided later).[web:21]
- Prepare your own `main.py` based on the example provided.
- Run the container with:
  - A bind mount for `main.py` into `/app/main.py`.
  - Environment variables for Home Assistant and Loxone connection details.

Example:

```bash
docker run -d 
--name ha-loxone-bridge 
-v /path/to/your/main.py:/app/main.py:ro 
-e HA_URL=http://homeassistant:8123 
-e HA_TOKEN=YOUR_LONG_LIVED_TOKEN 
-e LOXONE_HOST=loxone.local 
-e LOXONE_USER=loxone_user 
-e LOXONE_PASSWORD=loxone_password
ghcr.io/woziwrt/ha-loxone-bridge:runtime
```


This way you can freely edit your `main.py` (add entities, change behaviour) without rebuilding the Docker image.

### 2. Build your own image with `main.py` inside (advanced / optional)

If you prefer to have a self-contained image:

- Copy the provided `Dockerfile` and adjust it to include your `main.py`, for example:

```bash 
FROM ghcr.io/woziwrt/ha-loxone-bridge:runtime
COPY main.py /app/main.py
```

- Build your own image (locally or using GitHub Actions).
- Run it without mounting `main.py`:

```bash
docker run -d 
--name ha-loxone-bridge 
-e HA_URL=http://homeassistant:8123 
-e HA_TOKEN=YOUR_LONG_LIVED_TOKEN 
-e LOXONE_HOST=loxone.local 
-e LOXONE_USER=loxone_user 
-e LOXONE_PASSWORD=loxone_password
your-registry/ha-loxone-bridge:with-main
```


This is useful if you deploy the same bridge logic to multiple machines and do not want to manage separate `main.py` files.

## CI, multi-arch builds and testing

This repository will also include:

- A GitHub Actions workflow that:
  - Uses an ARM-based runner.
  - Builds a multi-architecture runtime image (amd64, arm64, arm).[web:21]
  - Runs a small smoke test: start a container with a simple test `main.py` and verify that it runs and exits cleanly.

- Release builds:
  - For selected tags, the workflow will publish runtime images to a container registry.[web:23]
  - Users can pull these images directly without setting up any local build environment.

The test scenario in CI will mirror the basic steps shown in this README, so if the workflow is green, the documented usage is expected to work as well.

## Adapting this to your own setup

This project is deliberately opinionated and focused on one concrete, working example:

- MikroTik RB5009 as the host.
- Home Assistant and the bridge in containers.
- A specific device (humidifier) as the reference use case.

If you want to use it with:

- Different MikroTik hardware,
- A Raspberry Pi,
- A NAS or any other Linux host,

you will need to:

- Recreate the “host side” (container configuration / `docker run` / docker-compose) for your platform.
- Adjust `main.py` to your own Home Assistant entities and Loxone setup.[web:26]
- Optionally, use the provided GitHub Actions workflow to build your own images.

Think of this repository as a documented blueprint and toolbox, not as a one-click integration for every environment.




