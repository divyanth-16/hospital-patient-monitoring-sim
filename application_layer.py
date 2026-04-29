"""
Layer 7 – Application Layer
============================
Generates medical sensor payloads and defines QoS / KPI targets.
"""

import numpy as np


# ── QoS Requirements ───────────────────────────────────────────────────────
QOS = {
    "max_e2e_delay_ms":    200,    # ms
    "min_throughput_kbps": 100,    # kbps
    "max_ber":             1e-5,
    "min_pdr":             0.99,
    "max_retransmissions": 3,
}

# ── KPI Definitions ────────────────────────────────────────────────────────
KPI = {
    "End-to-End Delay":  {"unit": "ms",    "target": "≤ 200"},
    "Throughput":        {"unit": "kbps",  "target": "≥ 100"},
    "BER":               {"unit": "ratio", "target": "≤ 1e-5"},
    "PDR":               {"unit": "%",     "target": "≥ 99"},
    "Retransmissions":   {"unit": "count", "target": "≤ 3"},
}

# ── Sensor Definitions ─────────────────────────────────────────────────────
SENSOR_TYPES = {
    "ECG":       {"unit": "mV",  "range": (0.5, 2.5),   "priority": "HIGH"},
    "HeartRate": {"unit": "bpm", "range": (40,  120),    "priority": "HIGH"},
    "Temp":      {"unit": "°C",  "range": (35.0, 40.0),  "priority": "MEDIUM"},
    "SpO2":      {"unit": "%",   "range": (85,  100),    "priority": "HIGH"},
}


def generate_payload(sensor_type: str) -> bytes:
    """Generate a UTF-8 encoded ASCII sensor reading payload."""
    info = SENSOR_TYPES[sensor_type]
    value = round(np.random.uniform(*info["range"]), 2)
    msg = f"TYPE={sensor_type};VALUE={value};UNIT={info['unit']};PRI={info['priority']}"
    return msg.encode("utf-8")


if __name__ == "__main__":
    for sensor in SENSOR_TYPES:
        payload = generate_payload(sensor)
        print(f"[{sensor}] {payload.decode()}")
