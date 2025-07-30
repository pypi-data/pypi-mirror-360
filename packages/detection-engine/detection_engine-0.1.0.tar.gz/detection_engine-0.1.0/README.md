# VPN & Tunnel Detection CLI Tool

[![PyPI version](https://img.shields.io/pypi/v/detection_engine)](https://pypi.org/project/detection_engine/)
[![Python version](https://img.shields.io/pypi/pyversions/detection_engine)](https://pypi.org/project/detection_engine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/detection_engine)](https://pepy.tech/project/detection_engine)

This project is a Python-based command-line tool that helps you detect whether an IP address is likely coming from a VPN, proxy, or abusive source. It uses a combination of IP metadata, ASN heuristics, and optional third-party API lookups for deeper inspection.

---

## Features
- Checks organization name and ASN for suspicious patterns
- Uses IPInfo (free) for geolocation and org info
- Integrates with [AbuseIPDB](https://www.abuseipdb.com/) and [IPQualityScore](https://ipqualityscore.com/) APIs for reputation checks (optional)
- Heuristic-based scoring system with confidence levels (Low / Moderate / High)
- CLI-based tool installable with `pip install` + global command `vpnscan`

---

## Installation
1. Clone the repository:
```bash
git clone https://github.com/your-username/vpn-tunnel-detector.git
cd vpn-tunnel-detector
```

2. Set up a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the module in editable mode:
```bash
pip install --editable .
```

This registers the `vpnscan` command globally in your environment.

---

## API Keys (Optional, for advanced detection)
To enable IP reputation scoring, manually add your API keys directly into these files:

**In `detection_engine/engine/abuseipdb_checker.py`**
```python
api_key = "your_actual_abuseipdb_api_key"
```

**In `detection_engine/engine/ipqualityscore_checker.py`**
```python
api_key = "your_actual_ipqs_api_key"
```

You can skip this step if you only want to use free detection features.

---

## Usage
Run the tool using:
```bash
scan --ip <IP_ADDRESS>
```
Example:
```bash
scan --ip 104.28.228.78
```

You’ll see output like this:
```
-------------------------- Welcome to the VPN & Tunnel Detection CLI Tool --------------------------

This tool checks if an IP address is associated with VPN, proxy, or tunneling services.
It uses multiple data sources to provide a comprehensive analysis.

You can cancel the operation at any time by pressing Ctrl+C.

Starting the detection process...

Analyzing IP: 100%|████████████████████████| 50/50 [00:00<00:00, 82.80it/s]

Detection Result
------------------
IP                : 104.28.228.78
ORG               : Cloudflare, Inc.
ASN               : AS13335
LOCATION          : Washington, US
IS SUSPICIOUS     : Yes
DETECTION REASON  : ASN AS13335 is frequently used by VPN or hosting providers. Org name includes 'cloud', commonly seen in VPN or hosting services.
ABUSE SCORE       : 100
IPQS FRAUD SCORE  : 100
CONFIDENCE LEVEL  : High
DISCLAIMER        : This result indicates whether the IP shows characteristics of VPN/proxy or abusive usage. It does not imply malicious intent. Many users use VPNs for privacy or remote work.
```

---

## Project Structure
```
```
pymod_detection_engine/
├── detection_engine/
│   ├── __init__.py
│   ├── run_engine.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── suspicious_asns.json
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── ipinfo_wrapper.py
│   │   ├── heuristics.py
│   │   ├── detection_engine.py
│   │   ├── abuseipdb_checker.py
│   │   └── ipqualityscore_checker.py
├── requirements.txt
├── setup.py
├── MANIFEST.in
└── README.md
```

---

## License
MIT License — free to use and modify with attribution.
