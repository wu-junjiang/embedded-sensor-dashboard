"""
sensor_read.py — reads a DHT22 temperature/humidity sensor and exposes
the latest reading for the dashboard to consume.

Hardware note: this is written against the `adafruit-circuitpython-dht`
library, the standard choice for DHT22 on Raspberry Pi. On a machine
without the actual sensor attached (e.g. while developing away from your
Pi), use the --mock flag to generate fake but plausible readings so you
can build/test the dashboard independently of the hardware.

Install (on the Pi):
    pip install adafruit-circuitpython-dht --break-system-packages

Run:
    python3 sensor_read.py          # real sensor on GPIO pin 4
    python3 sensor_read.py --mock   # fake data, no hardware required
"""

import argparse
import json
import random
import time
from pathlib import Path

READING_FILE = Path(__file__).parent / "latest_reading.json"


def read_real_sensor(pin=4):
    """Read from an actual DHT22 sensor. Only import the hardware library
    here (not at module level) so --mock mode works on machines without it
    installed."""
    import adafruit_dht
    import board

    dht_device = adafruit_dht.DHT22(getattr(board, f"D{pin}"))
    try:
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        return temperature_c, humidity
    except RuntimeError as e:
        # DHT sensors are notoriously flaky on individual reads — this is
        # expected occasionally, not a bug. Real production code retries.
        print(f"Sensor read error (will retry next cycle): {e}")
        return None, None


def read_mock_sensor():
    """Generate plausible fake readings for development without hardware."""
    temperature_c = round(random.uniform(18.0, 26.0), 1)
    humidity = round(random.uniform(30.0, 60.0), 1)
    return temperature_c, humidity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true",
                         help="Use fake sensor data instead of real hardware")
    parser.add_argument("--interval", type=float, default=2.0,
                         help="Seconds between readings")
    args = parser.parse_args()

    print(f"Starting sensor loop (mock={args.mock}). Writing readings to "
          f"{READING_FILE}. Ctrl+C to stop.")

    while True:
        if args.mock:
            temp, humidity = read_mock_sensor()
        else:
            temp, humidity = read_real_sensor()

        if temp is not None:
            reading = {
                "temperature_c": temp,
                "humidity_pct": humidity,
                "timestamp": time.time(),
            }
            READING_FILE.write_text(json.dumps(reading))
            print(f"Reading: {reading}")

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
