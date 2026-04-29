"""
Layer 2 – Data Link Layer
==========================
Frame delimiting and Stop-and-Wait ARQ.

Frame structure:
    [0xAA 0xBB] [length: 2B] [IP packet: N bytes] [0xCC 0xDD]
"""

import struct
import numpy as np


FRAME_START   = b"\xAA\xBB"
FRAME_END     = b"\xCC\xDD"
LENGTH_FORMAT = "!H"
LENGTH_SIZE   = struct.calcsize(LENGTH_FORMAT)


def build_frame(packet: bytes) -> bytes:
    """Wrap an IP packet in a Data Link frame."""
    length = struct.pack(LENGTH_FORMAT, len(packet))
    return FRAME_START + length + packet + FRAME_END


class DataLinkLayer:
    """
    Stop-and-Wait ARQ transmitter/receiver.

    Parameters
    ----------
    max_retries : int   Maximum retransmission attempts per frame (default 3)
    per         : float Simulated packet error rate  0.0 – 1.0  (default 0.1)
    """

    def __init__(self, max_retries: int = 3, per: float = 0.1):
        self.max_retries     = max_retries
        self.per             = per
        self.total_frames    = 0
        self.retransmissions = 0
        self.dropped_frames  = 0

    def transmit(self, packet: bytes, channel_fn) -> tuple:
        """
        Transmit one packet using Stop-and-Wait ARQ.

        Parameters
        ----------
        packet     : IP packet bytes to transmit
        channel_fn : callable(frame_bytes) → (received_bytes, bit_errors)
                     Represents the physical channel (BPSK + AWGN).

        Returns
        -------
        (success: bool, received_frame: bytes)
        """
        frame = build_frame(packet)

        for attempt in range(self.max_retries + 1):
            self.total_frames += 1
            received, _bit_errors = channel_fn(frame)

            # Simulate ACK loss / corruption via PER
            if np.random.rand() < self.per:
                if attempt < self.max_retries:
                    self.retransmissions += 1
                continue          # NACK — retransmit

            return True, received  # ACK received — success

        # Exhausted all retries
        self.dropped_frames += 1
        return False, b""

    @property
    def pdr(self) -> float:
        """Packet Delivery Ratio."""
        if self.total_frames == 0:
            return 1.0
        return 1.0 - (self.dropped_frames / self.total_frames)

    def stats(self) -> dict:
        return {
            "total_frames":    self.total_frames,
            "retransmissions": self.retransmissions,
            "dropped_frames":  self.dropped_frames,
            "pdr":             self.pdr,
        }


if __name__ == "__main__":
    sample_packet = b"\xC0\xA8\x0A\x01\xC0\xA8\x14\x01\x00\x0A" + b"HELLO"
    frame = build_frame(sample_packet)
    print(f"Packet size : {len(sample_packet)} bytes")
    print(f"Frame  size : {len(frame)} bytes")
    print(f"Frame  hex  : {frame.hex()}")
