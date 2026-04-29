"""
KPI Evaluation & Graph Generation
===================================
Simulates and plots the four KPI graphs:
    1. BER vs SNR
    2. Throughput vs SNR
    3. End-to-End Delay vs Number of Nodes
    4. Retransmissions vs Noise (PER)
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from physical_layer import theoretical_ber, bpsk_modulate, awgn_channel, bpsk_demodulate, bytes_to_bits


GRAPH_DIR = os.path.join(os.path.dirname(__file__), "..", "graphs")

COLORS = {
    "blue":   "#1A73E8",
    "red":    "#D32F2F",
    "green":  "#2E7D32",
    "orange": "#F57C00",
    "purple": "#6A1B9A",
}


def _save(fig, filename: str):
    os.makedirs(GRAPH_DIR, exist_ok=True)
    path = os.path.join(GRAPH_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ Saved → {path}")


# ── 1. BER vs SNR ─────────────────────────────────────────────────────────

def simulate_ber(snr_range: np.ndarray, n_bits: int = 10_000) -> list:
    bers = []
    for snr_db in snr_range:
        bits = np.random.randint(0, 2, n_bits).astype(float)
        rx   = bpsk_demodulate(awgn_channel(bpsk_modulate(bits), snr_db))
        ber  = np.mean(bits != rx)
        bers.append(max(ber, 1e-7))
    return bers


def plot_ber_vs_snr(snr_range=None):
    if snr_range is None:
        snr_range = np.arange(0, 16, 0.5)

    ber_sim  = simulate_ber(snr_range)
    ber_theo = theoretical_ber(snr_range)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(snr_range, ber_sim,  color=COLORS["blue"],  marker="o", ms=4,
                linewidth=1.8, label="Simulated BER (BPSK/AWGN)")
    ax.semilogy(snr_range, ber_theo, color=COLORS["red"],   linestyle="--",
                linewidth=1.8, label="Theoretical BER")
    ax.axhline(1e-5, color=COLORS["orange"], linestyle=":", linewidth=1.5,
               label="QoS BER Limit (10⁻⁵)")
    ax.set_xlabel("SNR (dB)", fontsize=12)
    ax.set_ylabel("Bit Error Rate (BER)", fontsize=12)
    ax.set_title("BER vs SNR – BPSK over AWGN", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.set_xlim(0, 15); ax.set_ylim(1e-7, 1)
    fig.tight_layout()
    _save(fig, "ber_vs_snr.png")


# ── 2. Throughput vs SNR ──────────────────────────────────────────────────

def simulate_throughput(snr_range: np.ndarray, payload_bytes: int = 64,
                        bit_rate_kbps: float = 1000.0) -> list:
    N = payload_bytes * 8
    throughputs = []
    for snr_db in snr_range:
        bits = np.random.randint(0, 2, N).astype(float)
        rx   = bpsk_demodulate(awgn_channel(bpsk_modulate(bits), snr_db))
        ber  = np.mean(bits != rx)
        prob = (1 - ber) ** N
        throughputs.append(bit_rate_kbps * prob)
    return throughputs


def plot_throughput_vs_snr(snr_range=None):
    if snr_range is None:
        snr_range = np.arange(0, 16, 0.5)

    tput = simulate_throughput(snr_range)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(snr_range, tput, color=COLORS["green"], linewidth=2, marker="s", ms=4,
            label="Throughput (kbps)")
    ax.axhline(100, color=COLORS["orange"], linestyle=":", linewidth=1.5,
               label="QoS Min (100 kbps)")
    ax.fill_between(snr_range, tput, 100,
                    where=[t < 100 for t in tput],
                    alpha=0.2, color="red", label="Below QoS threshold")
    ax.set_xlabel("SNR (dB)", fontsize=12)
    ax.set_ylabel("Throughput (kbps)", fontsize=12)
    ax.set_title("Throughput vs SNR – Smart Hospital System", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlim(0, 15)
    fig.tight_layout()
    _save(fig, "throughput_vs_snr.png")


# ── 3. E2E Delay vs Number of Nodes ──────────────────────────────────────

def simulate_delay(node_counts: list, base_ms: float = 5.0,
                   prop_ms: float = 2.0) -> list:
    delays = []
    for n in node_counts:
        hops  = max(1, int(np.log2(n)) + 1)
        delay = base_ms + hops * prop_ms + np.random.normal(0, 1)
        delays.append(max(delay, base_ms))
    return delays


def plot_delay_vs_nodes(node_range=None):
    if node_range is None:
        node_range = list(range(2, 31))

    delays = simulate_delay(node_range)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(node_range, delays, color=COLORS["purple"], linewidth=2,
            marker="D", ms=4, label="E2E Delay")
    ax.axhline(200, color=COLORS["red"], linestyle="--", linewidth=1.5,
               label="QoS Max Delay (200 ms)")
    ax.set_xlabel("Number of Nodes", fontsize=12)
    ax.set_ylabel("End-to-End Delay (ms)", fontsize=12)
    ax.set_title("E2E Delay vs Number of Nodes", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    _save(fig, "delay_vs_nodes.png")


# ── 4. Retransmissions vs Noise ───────────────────────────────────────────

def simulate_retransmissions(per_range: np.ndarray, n_frames: int = 200,
                              max_retry: int = 3) -> list:
    retrans = []
    for per in per_range:
        total = 0
        for _ in range(n_frames):
            for attempt in range(max_retry + 1):
                if np.random.rand() >= per:
                    break
                total += 1
        retrans.append(total / n_frames)
    return retrans


def plot_retransmissions_vs_noise(per_range=None):
    if per_range is None:
        per_range = np.arange(0, 0.55, 0.05)

    retrans = simulate_retransmissions(per_range)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(per_range, retrans, width=0.04, color=COLORS["blue"],
           edgecolor="white", alpha=0.85, label="Avg Retransmissions")
    ax.axhline(3, color=COLORS["red"], linestyle="--", linewidth=1.5,
               label="Max Retries = 3")
    ax.set_xlabel("Packet Error Rate (PER)", fontsize=12)
    ax.set_ylabel("Avg Retransmissions per Frame", fontsize=12)
    ax.set_title("Retransmissions vs Noise (Stop-and-Wait ARQ)", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    _save(fig, "retransmissions_vs_noise.png")


# ── Run all ───────────────────────────────────────────────────────────────

def generate_all_graphs(seed: int = 42):
    np.random.seed(seed)
    print("[KPI Graphs]")
    plot_ber_vs_snr()
    plot_throughput_vs_snr()
    plot_delay_vs_nodes()
    plot_retransmissions_vs_noise()
    print("All graphs generated.\n")


if __name__ == "__main__":
    generate_all_graphs()
