# HA–Loxone Bridge RB5009 example

This repository documents a concrete, working example of a custom bridge between Loxone and Home Assistant, running in containers on a MikroTik RB5009.

The goal is not to build a universal “works with everything” integration, but to provide a clean, reproducible blueprint you can adapt to your own setup:

- A minimal Docker‑based runtime image that executes a user‑provided `main.py` bridge script.
- An example deployment on a MikroTik RB5009 using RouterOS containers.
- A real‑world bridge script for one specific device (a humidifier) as a reference for your own logic.
- Example Loxone configuration with Virtual Inputs and Virtual Outputs, including screenshots.

All HTTP calls from Loxone go only to the local bridge service, so the Home Assistant bearer token never appears in the Loxone project.

---

## What this project is (and is not)

This project **provides**:

- A Docker runtime image with Python and required libraries, ready to run a user‑supplied `main.py`.
- A documented example of how the bridge can run on a MikroTik RB5009.
- Example bridge logic for one real device (humidifier) to serve as a starting point.
- Example VI/VO configuration in Loxone Config, with screenshots of the working setup.

This project **does not provide**:

- A generic bridge that automatically discovers and handles all Home Assistant entities.
- A complete, ready‑made configuration for every possible host (other MikroTiks, Raspberry Pi, NAS, …).
- A tutorial on how to program in Python or how to configure Home Assistant in general.

Think of this repository as a documented blueprint and toolbox, not as a one‑click integration for every environment. 

---

## High‑level architecture

At a high level, the setup looks like this:

- Home Assistant runs in a container, reachable at something like `http://homeassistant:8123`, using the standard port `8123`.
- The bridge runs in a separate container and talks to:
  - Home Assistant over its HTTP / WebSocket API, authenticated with a long‑lived token.
  - Loxone via its API / protocol using a Python library or direct requests.
- The actual bridge logic is implemented in a Python script `main.py`, which is **not** hard‑coded into the image.  
  The image only provides a stable runtime; you mount your own `main.py` from the host. 

All HTTP requests from Loxone are local to the bridge. Loxone never talks to Home Assistant directly and never sees the HA token.

---

## How to use this repository

There are two main ways to use this project.

### 1. Use the runtime image with your own `main.py` (recommended)

This is closest to how it runs on RB5009.

1. Build or pull the runtime image.
2. Prepare your own `main.py` based on the example in `examples/rb5009-humidifier`.
3. Run the container with:
   - a bind mount for `main.py` into `/app/main.py` (read‑only),
   - environment variables for Home Assistant and Loxone connection details.

Example:

```bash
docker run -d \
           --name ha-loxone-bridge \
           -v /path/on/host/main.py:/app/main.py:ro \
           -e HA_URL=http://homeassistant:8123 \
           -e HA_TOKEN=YOUR_LONG_LIVED_TOKEN \
           -e LOXONE_HOST=loxone.local \
           -e LOXONE_USER=loxone_user \
           -e LOXONE_PASSWORD=loxone_password \
           ghcr.io/woziwrt/ha-loxone-bridge:runtime
``` 



On a MikroTik RB5009 this is configured via the RouterOS container settings (environment, mounts, image), but the idea is the same:  
use one stable runtime image and keep your `main.py` and credentials on the host. 

This way you can freely edit `main.py` (add entities, change behaviour) without rebuilding the image.

### 2. Build your own image with `main.py` baked in (advanced / optional)

If you prefer a self‑contained image:

1. Copy the provided `Dockerfile` and adjust it to include your `main.py`, for example:

```bash 
FROM ghcr.io/woziwrt/ha-loxone-bridge:runtime
COPY main.py /app/main.py
```

2. Build your own image locally or via GitHub Actions.
3. Run it without mounting `main.py`:

```bash
docker run -d \ 
          --name ha-loxone-bridge \ 
          -e HA_URL=http://homeassistant:8123 \ 
          -e HA_TOKEN=YOUR_LONG_LIVED_TOKEN \ 
          -e LOXONE_HOST=loxone.local \ 
          -e LOXONE_USER=loxone_user \ 
          -e LOXONE_PASSWORD=loxone_password \
          your-registry/ha-loxone-bridge:with-main
```

This is useful when you want to deploy the same bridge logic to multiple machines and do not want to manage separate `main.py` files.

---

## RB5009 example – how we run it

In the `examples/rb5009-humidifier` directory you will find:

- A sample `main.py` implementing the bridge logic for one humidifier.
- Example RouterOS container configuration commands for running the bridge on a MikroTik RB5009.
- A snapshot of the firewall / NAT rules used in this setup. 

Command syntax and available options may differ between RouterOS versions, so treat the commands as a starting point and adapt them to your firmware.

---

## Loxone humidifier integration

The humidifier example focuses on one real device and shows, end‑to‑end, how it is integrated between Home Assistant and Loxone.

- Home Assistant exposes the humidifier as standard HA entities.
- The bridge maps these entities to Loxone Virtual Outputs (commands) and Virtual Inputs (status).
- Loxone Config uses only local HTTP calls to the bridge; no HA token is stored in the Loxone project. 

### Virtual Inputs – humidifier status

The screenshots in this section show how Virtual HTTP Inputs in Loxone are configured to read humidifier status via the bridge:

- ON/OFF state, target humidity, current humidity.
- Current mode, water state, availability state, error state.

Each VI uses a simple HTTP GET towards the bridge, and the bridge translates the response from Home Assistant into numeric values Loxone can work with. 

### Virtual Outputs – humidifier control

The Virtual Outputs are used to send commands from Loxone to the humidifier via the bridge:

- A single ON/OFF VO mapped to `/command/on?value=1` and `/command/on?value=0`.
- Several target humidity presets mapped to `/command/humidity?value=…`.
- Mode selection VOs mapped to `/command/mode?value=…`.

The screenshots illustrate the final set of VOs in Loxone Config and how they appear in LiveView.

---

## CI, multi‑arch builds and testing

A future CI workflow can:

- Use an ARM‑capable runner.
- Build a multi‑architecture runtime image (amd64, arm64, arm).
- Run a small smoke test by starting a container with a simple test `main.py` and verifying that it runs and exits cleanly.
- For tagged releases, publish runtime images to a container registry. 

If the workflow is green, the usage documented in this README is expected to work as well.

---

## Adapting this to your own setup

This project is deliberately opinionated and focused on one concrete, working example:

- MikroTik RB5009 as the host.
- Home Assistant and the bridge running in containers.
- A specific humidifier as the reference device.

To use it elsewhere you will need to:

- Recreate the host‑side container configuration (Docker / Docker Compose / RouterOS containers) for your platform.
- Adjust `main.py` to match your Home Assistant entities and Loxone setup.
- Optionally, use a CI workflow to build your own images. 

Use this repository as a documented blueprint and toolbox for your own HA ↔ Loxone bridges.

---

## License

This project is licensed under the MIT License – see the [`LICENSE`](./LICENSE) file for details.



