import os
import sys
import requests

def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value

HA_URL = get_env("HA_URL").rstrip("/")
HA_TOKEN = get_env("HA_TOKEN")

# Example entity ID of the humidifier in Home Assistant
HUMIDIFIER_ENTITY_ID = os.environ.get("HUMIDIFIER_ENTITY_ID", "humidifier.example")

def get_ha_state(entity_id: str) -> dict:
    url = f"{HA_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    resp = requests.get(url, headers=headers, timeout=5)
    resp.raise_for_status()
    return resp.json()

def main() -> None:
    try:
        state = get_ha_state(HUMIDIFIER_ENTITY_ID)
    except Exception as exc:
        print(f"Error talking to Home Assistant: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Humidifier {HUMIDIFIER_ENTITY_ID} state: {state.get('state')}")
    attrs = state.get("attributes", {})
    current_humidity = attrs.get("humidity")
    print(f"Current humidity: {current_humidity}")

if __name__ == "__main__":
    main()
