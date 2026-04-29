"""
main.py – Smart Hospital Patient Monitoring System
====================================================
Entry point. Runs the full OSI-layer pipeline for each sensor
and then generates all KPI graphs.

Usage:
    python main.py
"""

import sys
import os
import numpy as np

# Allow imports from src/ when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from application_layer import generate_payload, SENSOR_TYPES
from transport_layer   import create_segment, verify_segment, HEADER_SIZE as T_HEADER
from network_layer     import create_packet, get_route, get_destination, NODE_TABLE, HEADER_SIZE as N_HEADER
from datalink_layer    import DataLinkLayer
from physical_layer    import transmit_frame
from kpi_evaluation    import generate_all_graphs


def run_pipeline(sensor: str, snr_db: float = 10.0, per: float = 0.1):
    """Run the complete 5-layer pipeline for one sensor reading."""

    print(f"\n{'='*65}")
    print(f" SMART HOSPITAL – {sensor} SENSOR  (SNR={snr_db} dB, PER={int(per*100)}%)")
    print(f"{'='*65}")

    # ── Layer 7: Application ──────────────────────────────────────────────
    print("\n[L7 – APPLICATION]")
    payload = generate_payload(sensor)
    print(f"  Payload  : {payload.decode()}")
    print(f"  Size     : {len(payload)} bytes")

    # ── Layer 4: Transport ────────────────────────────────────────────────
    print("\n[L4 – TRANSPORT]")
    seq_num = np.random.randint(0, 65535)
    segment = create_segment(payload, seq_num)
    print(f"  Seq Num  : {seq_num}")
    print(f"  Segment  : {len(segment)} bytes  (4B header + {len(payload)}B payload)")

    # ── Layer 3: Network ──────────────────────────────────────────────────
    print("\n[L3 – NETWORK]")
    src   = f"{sensor}_Sensor"
    if src not in NODE_TABLE:
        src = "ECG_Sensor"
    dst   = get_destination(src)
    route = get_route(src)
    packet = create_packet(segment, src, dst)
    print(f"  Source   : {src}  [{NODE_TABLE[src]['ip']}]")
    print(f"  Dest     : {dst}  [{NODE_TABLE[dst]['ip']}]")
    print(f"  Route    : {src} → {' → '.join(route)}")
    print(f"  Packet   : {len(packet)} bytes")

    # ── Layer 2: Data Link (Stop-and-Wait ARQ) ────────────────────────────
    print("\n[L2 – DATA LINK  (Stop-and-Wait ARQ)]")
    dl = DataLinkLayer(max_retries=3, per=per)

    def channel_fn(data):
        return transmit_frame(data, snr_db)

    success, rx_frame = dl.transmit(packet, channel_fn)
    stats = dl.stats()
    print(f"  Retrans  : {stats['retransmissions']}")
    print(f"  PDR      : {stats['pdr']*100:.1f}%")
    print(f"  Delivered: {'YES ✓' if success else 'NO  ✗ (dropped)'}")

    # ── Layer 1: Physical (BPSK / AWGN) ──────────────────────────────────
    print("\n[L1 – PHYSICAL  (BPSK / AWGN)]")
    import numpy as _np
    from physical_layer import bytes_to_bits, bpsk_modulate, awgn_channel, bpsk_demodulate
    bits      = bytes_to_bits(packet)
    modulated = bpsk_modulate(bits)
    received  = awgn_channel(modulated, snr_db)
    decoded   = bpsk_demodulate(received)
    bit_errs  = int(_np.sum(bits != decoded))
    ber       = bit_errs / len(bits) if len(bits) > 0 else 0.0
    print(f"  Bits Tx  : {len(bits)}")
    print(f"  Bit Errs : {bit_errs}")
    print(f"  BER      : {ber:.2e}")

    # ── Receiver CRC Verification ─────────────────────────────────────────
    print("\n[RECEIVER – CRC VERIFICATION]")
    if success and len(rx_frame) > N_HEADER + T_HEADER:
        rx_segment = rx_frame[N_HEADER:]
        crc_ok, rx_payload, rx_seq = verify_segment(rx_segment)
        print(f"  CRC OK   : {'YES ✓' if crc_ok else 'NO  ✗'}")
        if crc_ok:
            try:
                print(f"  Data     : {rx_payload.decode('utf-8', errors='replace')}")
            except Exception:
                print(f"  Data     : (binary, {len(rx_payload)} bytes)")
    else:
        print("  Frame dropped or too short to verify.")


def main():
    np.random.seed(42)

    # Run pipeline for all four sensor types
    for sensor in SENSOR_TYPES:
        run_pipeline(sensor, snr_db=10.0, per=0.1)

    # Generate all KPI graphs
    print(f"\n{'='*65}")
    generate_all_graphs(seed=42)
    print("✓ Done. Graphs saved to graphs/")


if __name__ == "__main__":
    main()
