# Simulator (Smart Bins + Events)

## What it simulates

- **IR waste detection** (`ir_detected`)
- **Ultrasonic fill level** (`fill_level_pct`)
- **Load cell weight** (`weight_kg`)
- **Gas sensor** (`gas_ppm`)
- **Temp/Humidity** (`temperature_c`, `humidity_pct`)

Publishes telemetry to MQTT topic:

`bins/<bin_id>/telemetry`

## Run

```bash
cd simulator
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python smart_bin_simulator.py --bins 10 --interval 3
```

Optional: simulate AI classification from image URLs:

```bash
python image_event_simulator.py --bin-id BIN_001 --image-url https://.../image.jpg
```

