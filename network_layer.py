"""
Layer 3 – Network Layer
========================
IP addressing, node address table, and static shortest-path routing.
Wraps transport segments into simplified IP-like packets.
"""

import struct


# ── Node Address Table ─────────────────────────────────────────────────────
NODE_TABLE = {
    "ECG_Sensor":    {"ip": "192.168.10.1",   "mac": "AA:BB:CC:DD:00:01", "type": "Sensor",   "location": "Ward A"},
    "HR_Sensor":     {"ip": "192.168.10.2",   "mac": "AA:BB:CC:DD:00:02", "type": "Sensor",   "location": "Ward A"},
    "Temp_Sensor":   {"ip": "192.168.10.3",   "mac": "AA:BB:CC:DD:00:03", "type": "Sensor",   "location": "Ward B"},
    "SpO2_Sensor":   {"ip": "192.168.10.4",   "mac": "AA:BB:CC:DD:00:04", "type": "Sensor",   "location": "Ward B"},
    "Router":        {"ip": "192.168.10.254", "mac": "AA:BB:CC:DD:FF:FE", "type": "Router",   "location": "Server Room"},
    "NurseStation":  {"ip": "192.168.20.1",   "mac": "AA:BB:CC:DD:10:01", "type": "Server",   "location": "Nurse Desk"},
    "CentralServer": {"ip": "10.0.0.100",     "mac": "AA:BB:CC:DD:20:01", "type": "Server",   "location": "Data Centre"},
}

# ── Static Routing Table (Shortest Path) ──────────────────────────────────
# All paths are 2 hops: Sensor → Router → Destination
STATIC_ROUTES = {
    "ECG_Sensor":  ["Router", "NurseStation"],
    "HR_Sensor":   ["Router", "NurseStation"],
    "Temp_Sensor": ["Router", "CentralServer"],
    "SpO2_Sensor": ["Router", "NurseStation"],
}

# ── Packet format: src_ip(4B) + dst_ip(4B) + length(2B) ──────────────────
PACKET_FORMAT = "!4s4sH"
HEADER_SIZE   = struct.calcsize(PACKET_FORMAT)


def ip_to_bytes(ip: str) -> bytes:
    return bytes(int(x) for x in ip.split("."))


def create_packet(segment: bytes, src_node: str, dst_node: str) -> bytes:
    """
    Encapsulate a transport segment into a network packet.

    Packet structure:
        [src_ip: 4B] [dst_ip: 4B] [length: 2B] [segment: N bytes]
    """
    src_ip = ip_to_bytes(NODE_TABLE[src_node]["ip"])
    dst_ip = ip_to_bytes(NODE_TABLE[dst_node]["ip"])
    header = struct.pack(PACKET_FORMAT, src_ip, dst_ip, len(segment))
    return header + segment


def get_route(src_node: str) -> list:
    """Return the static route (list of hops) for a given source node."""
    return STATIC_ROUTES.get(src_node, [])


def get_destination(src_node: str) -> str:
    """Return the final destination node for a given source."""
    route = get_route(src_node)
    return route[-1] if route else "NurseStation"


def print_node_table():
    """Pretty-print the node address table."""
    header = f"{'Node':<16} {'IP Address':<18} {'MAC Address':<20} {'Type':<8} {'Location'}"
    print(header)
    print("-" * len(header))
    for name, info in NODE_TABLE.items():
        print(f"{name:<16} {info['ip']:<18} {info['mac']:<20} {info['type']:<8} {info['location']}")


if __name__ == "__main__":
    print_node_table()
    print()
    for src in STATIC_ROUTES:
        route = get_route(src)
        print(f"Route: {src} → {' → '.join(route)}")
