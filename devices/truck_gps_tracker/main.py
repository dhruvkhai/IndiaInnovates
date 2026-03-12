"""
Garbage Truck GPS Tracker (Raspberry Pi + NEO-6M)

Behavior:
1) Read NMEA sentences from serial (NEO-6M).
2) Parse latitude/longitude.
3) Send truck location to backend API every 10 seconds.

Default serial device:
  /dev/serial0  (common on Raspberry Pi UART)

Install:
  pip install -r requirements.txt

Run:
  python main.py --truck-id TRUCK_01 --serial /dev/serial0 --baud 9600

Backend:
- By default this script sends the JSON shape you requested:
  {
    "truck_id": "...",
    "latitude": 18.5204,
    "longitude": 73.8567,
    "timestamp": "ISO timestamp"
  }

- If you want to POST directly into THIS repo's backend endpoint `/trucks/location`,
  pass `--backend-mode repo` which will send:
  { "truck_id", "lat", "lng", "status", "ts" }
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

import httpx
import pynmea2
import serial


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def open_serial(port: str, baud: int) -> serial.Serial:
    return serial.Serial(port=port, baudrate=baud, timeout=1)


def read_fix(ser: serial.Serial) -> tuple[float, float] | None:
    """
    Returns (lat, lon) when a valid fix is found; otherwise None.
    Parses GGA/RMC sentences.
    """
    line = ser.readline().decode(errors="ignore").strip()
    if not line.startswith("$"):
        return None

    try:
        msg = pynmea2.parse(line)
    except pynmea2.ParseError:
        return None

    # RMC and GGA are most common for position
    # - RMC has status 'A' for active
    # - GGA has gps_qual > 0 for fix
    if msg.sentence_type == "RMC":
        status = getattr(msg, "status", None)
        if status != "A":
            return None
        lat = getattr(msg, "latitude", None)
        lon = getattr(msg, "longitude", None)
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)

    if msg.sentence_type == "GGA":
        gps_qual = getattr(msg, "gps_qual", 0) or 0
        if int(gps_qual) <= 0:
            return None
        lat = getattr(msg, "latitude", None)
        lon = getattr(msg, "longitude", None)
        if lat is None or lon is None:
            return None
        return float(lat), float(lon)

    return None


def post_location(
    client: httpx.Client,
    backend_url: str,
    truck_id: str,
    lat: float,
    lon: float,
    backend_mode: str,
) -> None:
    if backend_mode == "repo":
        payload = {
            "truck_id": truck_id,
            "lat": lat,
            "lng": lon,
            "status": "en_route",
            "ts": iso_utc_now(),
        }
        url = backend_url.rstrip("/") + "/trucks/location"
    else:
        payload = {
            "truck_id": truck_id,
            "latitude": lat,
            "longitude": lon,
            "timestamp": iso_utc_now(),
        }
        url = backend_url.rstrip("/")

    r = client.post(url, json=payload)
    r.raise_for_status()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--truck-id", required=True)
    p.add_argument("--serial", default="/dev/serial0")
    p.add_argument("--baud", type=int, default=9600)
    p.add_argument("--interval", type=float, default=10.0)
    p.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Base backend URL (repo mode) or full endpoint URL (generic mode).",
    )
    p.add_argument(
        "--backend-mode",
        choices=["repo", "generic"],
        default="repo",
        help="repo: POST to /trucks/location (this repo's backend). generic: POST to backend-url directly with latitude/longitude keys.",
    )
    args = p.parse_args()

    print(f"[GPS] Truck={args.truck_id} Serial={args.serial}@{args.baud} Interval={args.interval}s")
    print(f"[GPS] Backend mode={args.backend_mode} Backend URL={args.backend_url}")

    ser = open_serial(args.serial, args.baud)
    last_sent = 0.0

    with httpx.Client(timeout=5) as client:
        while True:
            fix = read_fix(ser)
            now = time.time()

            if fix and (now - last_sent) >= args.interval:
                lat, lon = fix
                try:
                    post_location(client, args.backend_url, args.truck_id, lat, lon, args.backend_mode)
                    print(f"[GPS] Sent {lat:.6f}, {lon:.6f} at {iso_utc_now()}")
                except Exception as e:
                    print(f"[GPS] POST failed: {e}")
                last_sent = now


if __name__ == "__main__":
    main()

