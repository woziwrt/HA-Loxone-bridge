import os
import requests

HA_URL = os.environ["HA_URL"]
HA_TOKEN = os.environ["HA_TOKEN"]
LOXONE_HOST = os.environ["LOXONE_HOST"]
LOXONE_USER = os.environ["LOXONE_USER"]
LOXONE_PASSWORD = os.environ["LOXONE_PASSWORD"]

# TODO: implement real logic:
# - read Loxone virtual inputs (desired humidity, on/off)
# - call Home Assistant services to control the humidifier
# - push state back to Loxone virtual outputs

print("Example humidifier bridge stub started.")
