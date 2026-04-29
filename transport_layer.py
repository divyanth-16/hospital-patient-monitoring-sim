"""
Layer 4 – Transport Layer
==========================
Adds CRC-16 checksum and sequence number to application payloads.
Provides segment creation and verification (error detection).
"""

import struct


HEADER_FORMAT = "!HH"                        # seq_num (2B) + CRC-16 (2B)
HEADER_SIZE   = struct.calcsize(HEADER_FORMAT)


def crc16(data: bytes) -> int:
    """Compute CRC-16 using polynomial 0xA001 (reflected 0x8005)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def create_segment(payload: bytes, seq_num: int) -> bytes:
    """
    Encapsulate payload into a transport segment.

    Segment structure:
        [seq_num: 2B] [CRC-16: 2B] [payload: N bytes]
    """
    checksum = crc16(payload)
    header   = struct.pack(HEADER_FORMAT, seq_num, checksum)
    return header + payload


def verify_segment(segment: bytes) -> tuple:
    """
    Verify CRC and extract payload from a received segment.

    Returns:
        (crc_ok: bool, payload: bytes, seq_num: int)
    """
    seq_num, crc_recv = struct.unpack(HEADER_FORMAT, segment[:HEADER_SIZE])
    payload           = segment[HEADER_SIZE:]
    crc_calc          = crc16(payload)
    return (crc_recv == crc_calc), payload, seq_num


if __name__ == "__main__":
    sample  = b"TYPE=ECG;VALUE=1.25;UNIT=mV;PRI=HIGH"
    seg     = create_segment(sample, seq_num=42)
    ok, pl, seq = verify_segment(seg)
    print(f"Segment size : {len(seg)} bytes")
    print(f"Seq Num      : {seq}")
    print(f"CRC OK       : {ok}")
    print(f"Payload      : {pl.decode()}")
