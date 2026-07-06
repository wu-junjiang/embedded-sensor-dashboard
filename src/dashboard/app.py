"""
app.py — minimal Flask dashboard showing the latest sensor reading.

Run alongside sensor_read.py (in a separate terminal/process):
    python3 sensor_read.py --mock &
    python3 dashboard/app.py

Then open http://localhost:5000 in a browser.

Install:
    pip install flask --break-system-packages
"""

import json
from pathlib import Path

from flask import Flask, jsonify, render_template

app = Flask(__name__)
READING_FILE = Path(__file__).parent.parent / "latest_reading.json"


def get_latest_reading():
    if not READING_FILE.exists():
        return {"temperature_c": None, "humidity_pct": None, "timestamp": None}
    return json.loads(READING_FILE.read_text())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/latest")
def api_latest():
    """Frontend polls this endpoint to update the dashboard live."""
    return jsonify(get_latest_reading())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
