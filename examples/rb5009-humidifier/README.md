# RB5009 humidifier example

This example documents the configuration used to run the HA–Loxone bridge on a MikroTik RB5009 for one real device – a Levoit 6000S humidifier.

It shows how the generic bridge runtime is used in a concrete installation:

- Home Assistant running in a container on the RB5009.
- The bridge running in a separate container on the same host.
- Loxone connected via Virtual Inputs and Virtual Outputs to the bridge, not directly to Home Assistant. [file:62]

Use this as a reference when building your own device‑specific bridge scripts and RouterOS container configuration.

---

## Contents

This directory contains:

- `main.py` – a sample bridge script for the humidifier.
- RouterOS container configuration commands for running the bridge on an RB5009.
- A snapshot of firewall / NAT rules used in this setup.
- References back to the main `README.md` with screenshots of the Loxone configuration. [file:62]

The script and commands are intentionally minimal and focused on one device, so they stay easy to read and adapt.

---

## Bridge behaviour (humidifier)

In this example, the bridge:

- Connects to Home Assistant using `HAURL` and `HATOKEN` environment variables.
- Exposes simple HTTP endpoints (`/state/...`, `/command/...`) for Loxone to call.
- Translates between:
  - Home Assistant humidifier entities and attributes.
  - Loxone Virtual Inputs (status) and Virtual Outputs (commands).

Typical mapping:

- VI for ON/OFF status, target humidity, current humidity, mode, water state, availability and error state.
- VO for:
  - ON/OFF (`/command/on?value=1` / `/command/on?value=0`).
  - Target humidity presets (`/command/humidity?value=…`).
  - Mode selection (`/command/mode?value=auto|humidity|normal|sleep`). [file:61]

The goal is to keep the HTTP interface as simple as possible from Loxone’s perspective:  
Loxone only sees numeric values and a small set of HTTP paths.

---

## RouterOS container configuration

The included RouterOS commands illustrate:

- How the image is pulled onto the RB5009.
- How volumes and environment variables are configured.
- How the `main.py` is mounted into `/app/main.py` inside the bridge container.
- Basic firewall / NAT rules that allow Loxone to reach the bridge while keeping Home Assistant internal. [file:62]

RouterOS syntax and features can differ between firmware versions.  
Treat the commands here as a starting point and adjust them to match your RouterOS version and network layout.

---

## Using this example as a template

To adapt this example for your own setup:

1. Copy `main.py` and adjust:
   - Home Assistant entity IDs.
   - Any device‑specific logic (modes, value ranges, error handling).
2. Copy or adapt the RouterOS container configuration to your RB5009 (or equivalent Docker run commands on other hosts).
3. Recreate the Virtual Inputs and Outputs in your Loxone Config based on the screenshots and descriptions in the main `README.md`.
4. Test end‑to‑end:
   - Loxone → bridge → Home Assistant → humidifier.
   - Humidifier / Home Assistant state → bridge → Loxone VI. [file:61][file:62]

Once it works for one device, you can extend the same pattern for additional entities or other hardware.
