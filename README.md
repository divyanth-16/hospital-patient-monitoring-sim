# 🏥 Smart Hospital Patient Monitoring System
### Telecommunication & Networking Assignment — 10 Marks

> Real-time IoT medical data transmission simulation covering all five OSI layers with BPSK modulation, AWGN channel, Stop-and-Wait ARQ, and static routing.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [OSI Layer Breakdown](#osi-layer-breakdown)
4. [Project Structure](#project-structure)
5. [Setup & Running](#setup--running)
6. [Sample Output](#sample-output)
7. [KPI Graphs](#kpi-graphs)
8. [Node Address Table](#node-address-table)

---

## Project Overview

This project simulates a **Smart Hospital Patient Monitoring System** where multiple IoT medical sensors (ECG, Heart Rate, Temperature, SpO2) transmit real-time data to a nurse station and central server. The simulation models all five layers of the OSI model.

| Component       | Technology Used            |
|-----------------|----------------------------|
| Modulation      | BPSK (Binary Phase Shift Keying) |
| Channel Model   | AWGN (Additive White Gaussian Noise) |
| ARQ Protocol    | Stop-and-Wait              |
| Routing         | Static / Shortest Path     |
| Error Detection | CRC-16                     |
| Language        | Python 3.10+               |

---

## System Architecture

```
[ECG Sensor]   [HR Sensor]   [Temp Sensor]  [SpO2 Sensor]
      │               │              │               │
      └───────────────┴──────────────┴───────────────┘
                              │
                         [Router]
                        /         \
               [NurseStation]  [CentralServer]
```

---

## OSI Layer Breakdown

| Layer | Name         | Implementation                             |
|-------|--------------|--------------------------------------------|
| 7     | Application  | Sensor data generation, QoS/KPI definition |
| 4     | Transport    | CRC-16 checksum, sequence numbering        |
| 3     | Network      | IP addressing, static routing table        |
| 2     | Data Link    | Stop-and-Wait ARQ, frame delimiting        |
| 1     | Physical     | BPSK modulation over AWGN channel          |

---

## Setup & Running

### Prerequisites
```bash
pip install numpy matplotlib scipy
```

### Run Simulation
```bash
python src/simulation.py
```

This will:
1. Simulate data transmission for all 4 sensor types
2. Display layer-by-layer output in the terminal
3. Generate all 4 KPI graphs in `graphs/`

---

## Sample Output

```
=================================================================
 SMART HOSPITAL PATIENT MONITORING – FULL STACK SIMULATION
=================================================================

[LAYER 7 – APPLICATION]
  Sensor   : ECG
  Payload  : TYPE=ECG;VALUE=1.25;UNIT=mV;PRI=HIGH
  Size     : 36 bytes

[LAYER 4 – TRANSPORT]
  Seq Num  : 860
  CRC-16   : 0xC888
  Segment  : 40 bytes  (header=4B + payload)

[LAYER 3 – NETWORK]
  Source   : ECG_Sensor  [192.168.10.1]
  Dest     : NurseStation  [192.168.20.1]
  Route    : ECG_Sensor → Router → NurseStation
  Packet   : 50 bytes

[LAYER 2 – DATA LINK  (Stop-and-Wait ARQ)]
  PER      : 10%
  Retrans  : 0
  PDR      : 100.0%
  Delivered: YES ✓

[LAYER 1 – PHYSICAL  (BPSK / AWGN)]
  SNR      : 10.0 dB
  Modulation: BPSK
  Channel  : AWGN
  Bits Tx  : 400
  Bit Errs : 0
  BER      : 0.00e+00
```

---

## KPI Graphs

| Graph | Description |
|-------|-------------|
| `ber_vs_snr.png` | BER vs SNR (Simulated vs Theoretical BPSK) |
| `throughput_vs_snr.png` | Throughput vs SNR with QoS threshold |
| `delay_vs_nodes.png` | E2E Delay growth with network size |
| `retransmissions_vs_noise.png` | Stop-and-Wait ARQ retransmissions vs PER |

---

## Node Address Table

| Node          | IP Address       | MAC Address         | Type   |
|---------------|------------------|---------------------|--------|
| ECG_Sensor    | 192.168.10.1     | AA:BB:CC:DD:00:01   | Sensor |
| HR_Sensor     | 192.168.10.2     | AA:BB:CC:DD:00:02   | Sensor |
| Temp_Sensor   | 192.168.10.3     | AA:BB:CC:DD:00:03   | Sensor |
| SpO2_Sensor   | 192.168.10.4     | AA:BB:CC:DD:00:04   | Sensor |
| Router        | 192.168.10.254   | AA:BB:CC:DD:FF:FE   | Router |
| NurseStation  | 192.168.20.1     | AA:BB:CC:DD:10:01   | Server |
| CentralServer | 10.0.0.100       | AA:BB:CC:DD:20:01   | Server |

---

## QoS Requirements

| Metric              | Target         |
|---------------------|----------------|
| Max E2E Delay       | ≤ 200 ms       |
| Min Throughput      | ≥ 100 kbps     |
| Max BER             | ≤ 10⁻⁵         |
| Min PDR             | ≥ 99%          |
| Max Retransmissions | ≤ 3 per frame  |

---

*Assignment — Telecommunication and Networking | Smart Hospital Patient Monitoring System*
