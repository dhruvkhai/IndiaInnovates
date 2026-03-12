import argparse
import os

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend-url", default=os.getenv("BACKEND_URL", "http://localhost:8000"))
    parser.add_argument("--bin-id", required=True)
    parser.add_argument("--image-url", required=True)
    args = parser.parse_args()

    # Calls backend convenience endpoint which forwards to AI service
    with httpx.Client(timeout=30) as client:
        r = client.post(
            f"{args.backend_url}/classifications/ai/classify",
            params={"bin_id": args.bin_id, "image_url": args.image_url},
        )
        r.raise_for_status()
        print(r.json())


if __name__ == "__main__":
    main()

