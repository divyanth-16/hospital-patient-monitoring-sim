"""
Layer 1 – Physical Layer
=========================
BPSK modulation / demodulation over an AWGN channel.

BPSK mapping:
    bit 0  →  symbol –1  (phase 180°)
    bit 1  →  symbol +1  (phase   0°)

AWGN noise:
    n ~ N(0, σ²)  where  σ² = 1 / (2 · SNR_linear)

Demodulation (threshold at 0):
    received ≥ 0  →  bit 1
    received  < 0  →  bit 0
"""

import numpy as np


# ── Bit / Byte Conversion ──────────────────────────────────────────────────

def bytes_to_bits(data: bytes) -> np.ndarray:
    """Convert bytes to a numpy array of bits (float64)."""
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8)).astype(float)


def bits_to_bytes(bits: np.ndarray) -> bytes:
    """Convert a numpy bit array back to bytes (pads to multiple of 8)."""
    bits_int = np.clip(bits, 0, 1).astype(np.uint8)
    pad      = (8 - len(bits_int) % 8) % 8
    bits_int = np.concatenate([bits_int, np.zeros(pad, dtype=np.uint8)])
    return np.packbits(bits_int).tobytes()


# ── BPSK Modulation ────────────────────────────────────────────────────────

def bpsk_modulate(bits: np.ndarray) -> np.ndarray:
    """Map bits {0,1} → BPSK symbols {-1,+1}."""
    return 2.0 * bits - 1.0


def bpsk_demodulate(received: np.ndarray) -> np.ndarray:
    """Threshold decision: ≥ 0 → 1, < 0 → 0."""
    return (received >= 0).astype(float)


# ── AWGN Channel ───────────────────────────────────────────────────────────

def awgn_channel(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Pass signal through AWGN channel.

    Parameters
    ----------
    signal : modulated symbols
    snr_db : Signal-to-Noise Ratio in dB

    Returns
    -------
    Noisy received signal.
    """
    snr_linear = 10 ** (snr_db / 10.0)
    noise_std  = np.sqrt(1.0 / (2.0 * snr_linear))
    noise      = np.random.normal(0, noise_std, signal.shape)
    return signal + noise


# ── Full Frame Transmission ────────────────────────────────────────────────

def transmit_frame(data: bytes, snr_db: float) -> tuple:
    """
    Modulate, pass through AWGN, and demodulate a byte sequence.

    Returns
    -------
    (received_bytes: bytes, bit_errors: int)
    """
    bits      = bytes_to_bits(data)
    modulated = bpsk_modulate(bits)
    received  = awgn_channel(modulated, snr_db)
    decoded   = bpsk_demodulate(received)
    bit_errors = int(np.sum(bits != decoded))
    return bits_to_bytes(decoded), bit_errors


# ── Theoretical BER ────────────────────────────────────────────────────────

def theoretical_ber(snr_db_array) -> np.ndarray:
    """
    Theoretical BER for BPSK over AWGN:
        BER = 0.5 * erfc( sqrt(Eb/N0) )
    """
    from scipy.special import erfc
    snr_lin = 10 ** (np.asarray(snr_db_array) / 10.0)
    return 0.5 * erfc(np.sqrt(snr_lin))


if __name__ == "__main__":
    test_data  = b"ECG;1.25mV"
    rx, errors = transmit_frame(test_data, snr_db=10.0)
    print(f"Original : {test_data.hex()}")
    print(f"Received : {rx[:len(test_data)].hex()}")
    print(f"Bit errors: {errors}  /  {len(test_data)*8} bits")
