# -*- coding: utf-8 -*-
from flask import Flask, Response, request
import os
import requests
import traceback

HA_URL = os.getenv("HA_URL", "http://172.18.0.2:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "PUT_HERE_YOUR_HA_TOKEN")
ENTITY_ID = os.getenv("ENTITY_ID", "humidifier.superior_6000s")

app = Flask(__name__)

MODE_TO_NUM = {
    "auto": 1,
    "humidity": 2,  # Developer Tools modes: auto, humidity, normal, sleep
    "normal": 3,
    "sleep": 4,
}

NUM_TO_MODE = {
    1: "auto",
    2: "humidity",
    3: "normal",
    4: "sleep",
}


def ha_headers():
    return {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }


def ha_get_entity():
    r = requests.get(
        f"{HA_URL}/api/states/{ENTITY_ID}",
        headers=ha_headers(),
        timeout=5,
    )
    print("HA GET state response:", r.status_code, repr(r.text))
    r.raise_for_status()
    return r.json()


def ha_call_service(domain: str, service: str, payload: dict):
    url = f"{HA_URL}/api/services/{domain}/{service}"
    print("HA CALL SERVICE:", url, "payload:", repr(payload))
    r = requests.post(
        url,
        headers=ha_headers(),
        json=payload,
        timeout=5,
    )
    print("HA POST response:", r.status_code, repr(r.text))
    r.raise_for_status()
    return r.json()


def _response_int(value: int, status: int = 200):
    return Response(str(int(value)), mimetype="text/plain", status=status)


# ---------- STATE ENDPOINTS (READ) ----------


@app.route("/humidifier/state")
def humidifier_state():
    try:
        data = ha_get_entity()
        state = data.get("state")
        print("humidifier.state =", repr(state))
        return _response_int(1 if state == "on" else 0)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in humidifier_state:", repr(e))
        return _response_int(0, status=500)


@app.route("/state/on")
def state_on():
    """Logical state: 1 = on, 0 = otherwise."""
    try:
        data = ha_get_entity()
        state = data.get("state")
        return _response_int(1 if state == "on" else 0)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in state_on:", repr(e))
        return _response_int(0, status=500)


@app.route("/state/humidity")
def state_humidity():
    """Current humidity in % (current_humidity or humidity)."""
    try:
        data = ha_get_entity()
        attrs = data.get("attributes", {})
        value = attrs.get("current_humidity", attrs.get("humidity"))
        print("state_humidity =", repr(value))
        if value is None:
            raise ValueError("humidity attribute missing")
        return _response_int(round(float(value)))
    except Exception as e:
        traceback.print_exc()
        print("ERROR in state_humidity:", repr(e))
        return _response_int(0, status=500)


@app.route("/state/target_humidity")
def state_target_humidity():
    """Target humidity in % (attributes.humidity)."""
    try:
        data = ha_get_entity()
        attrs = data.get("attributes", {})
        value = attrs.get("humidity")
        print("state_target_humidity =", repr(value))
        if value is None:
            raise ValueError("target humidity attribute missing")
        return _response_int(round(float(value)))
    except Exception as e:
        traceback.print_exc()
        print("ERROR in state_target_humidity:", repr(e))
        return _response_int(0, status=500)


@app.route("/state/mode")
def state_mode():
    """Mode as number: auto=1, humidity=2, normal=3, sleep=4, else 0."""
    try:
        data = ha_get_entity()
        attrs = data.get("attributes", {})
        mode = attrs.get("mode")
        print("state_mode =", repr(mode))
        num = MODE_TO_NUM.get(str(mode).lower(), 0)
        return _response_int(num)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in state_mode:", repr(e))
        return _response_int(0, status=500)


@app.route("/state/available")
def state_available():
    """Availability: 1 = available, 0 = unavailable."""
    try:
        data = ha_get_entity()
        state = data.get("state")
        print("state_available.state =", repr(state))
        return _response_int(0 if state == "unavailable" else 1)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in state_available:", repr(e))
        return _response_int(0, status=500)


@app.route("/state/water")
def state_water():
    """Water status: 1 = water OK, 0 = problem."""
    try:
        data = ha_get_entity()
        state = data.get("state")
        print("state_water.state =", repr(state))
        # Basic assumption: if the device is on, water is OK.
        return _response_int(1 if state == "on" else 0)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in state_water:", repr(e))
        return _response_int(0, status=500)


@app.route("/state/error")
def state_error():
    """Error status: 1 = error/unavailable, 0 = OK."""
    try:
        data = ha_get_entity()
        state = data.get("state")
        print("state_error.state =", repr(state))
        error = 1 if state == "unavailable" else 0
        return _response_int(error)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in state_error:", repr(e))
        return _response_int(1, status=500)


# ---------- COMMAND ENDPOINTS (WRITE) ----------

@app.route("/command/on")
def command_on():
    """
    Control on/off state.
    Query param: value=1 -> ON, value=0 -> OFF.
    Returns: 1 on success, 0 on error.
    """
    try:
        raw = request.args.get("value")
        print("/command/on value =", repr(raw))
        if raw is None:
            raise ValueError("missing 'value' query parameter")

        v = int(raw)
        if v not in (0, 1):
            raise ValueError("value must be 0 or 1")

        if v == 1:
            # Request ON via input_boolean; HA automation will call humidifier.turn_on
            ha_call_service(
                "input_boolean",
                "turn_on",
                {"entity_id": "input_boolean.test_switch"},
            )
        else:
            # Request OFF via input_boolean; HA automation will call double-off script
            ha_call_service(
                "input_boolean",
                "turn_off",
                {"entity_id": "input_boolean.test_switch"},
            )

        return _response_int(1)

    except Exception as e:
        traceback.print_exc()
        print("ERROR in command_on:", repr(e))
        return _response_int(0, status=500)



@app.route("/command/target_humidity")
def command_target_humidity():
    """
    Set target humidity in percent.
    Query param: value=30..70 (example range).
    Returns: 1 on success, 0 on error.
    """
    try:
        raw = request.args.get("value")
        print("/command/target_humidity value =", repr(raw))
        if raw is None:
            raise ValueError("missing 'value' query parameter")

        humidity = int(raw)
        # Optional clamp, adjust if needed:
        if humidity < 30 or humidity > 70:
            print("Clamping humidity to 30..70 range")
            humidity = max(30, min(70, humidity))

        payload = {
            "entity_id": ENTITY_ID,
            "humidity": humidity,
        }
        ha_call_service("humidifier", "set_humidity", payload)
        return _response_int(1)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in command_target_humidity:", repr(e))
        return _response_int(0, status=500)


@app.route("/command/mode")
def command_mode():
    """
    Set mode based on numeric code.
    Query param: value=1..4 › auto/humidity/normal/sleep.
    Returns: 1 on success, 0 on error.
    """
    try:
        raw = request.args.get("value")
        print("/command/mode value =", repr(raw))
        if raw is None:
            raise ValueError("missing 'value' query parameter")

        code = int(raw)
        mode = NUM_TO_MODE.get(code)
        if mode is None:
            raise ValueError(f"unsupported mode code: {code}")

        payload = {
            "entity_id": ENTITY_ID,
            "mode": mode,
        }
        # Adjust service name if your integration uses a different one
        ha_call_service("humidifier", "set_mode", payload)
        return _response_int(1)
    except Exception as e:
        traceback.print_exc()
        print("ERROR in command_mode:", repr(e))
        return _response_int(0, status=500)


@app.route("/ping")
def ping():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
