import argparse
import os
import random
import time

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend-url", default=os.getenv("BACKEND_URL", "http://localhost:8000"))
    parser.add_argument("--trucks", type=int, default=3)
    parser.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()

    # Roughly around Delhi for demo
    base_lat, base_lng = 28.6139, 77.2090
    trucks = [
        {
            "truck_id": f"TRUCK_{i+1:02d}",
            "lat": base_lat + random.uniform(-0.03, 0.03),
            "lng": base_lng + random.uniform(-0.03, 0.03),
        }
        for i in range(args.trucks)
    ]

    with httpx.Client(timeout=10) as client:
        while True:
            for t in trucks:
                t["lat"] += random.uniform(-0.002, 0.002)
                t["lng"] += random.uniform(-0.002, 0.002)
                status = random.choice(["idle", "en_route", "collecting"])
                client.post(
                    f"{args.backend_url}/trucks/location",
                    json={
                        "truck_id": t["truck_id"],
                        "lat": t["lat"],
                        "lng": t["lng"],
                        "status": status,
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    },
                )
            time.sleep(args.interval)


if __name__ == "__main__":
    main()

