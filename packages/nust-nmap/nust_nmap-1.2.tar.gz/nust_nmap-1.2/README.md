<h1 align="center">nust-nmap</h1>
<p align="center">
    <img src="https://badge.fury.io/py/nust-nmap.svg" alt="PyPI version" />
    <img src="https://img.shields.io/pypi/pyversions/nust-nmap.svg" alt="Python versions" />
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
    <img src="https://pepy.tech/badge/nust-nmap" alt="Downloads" />
</p>



A robust, type-safe Python library providing an intuitive interface to the Nmap network scanning tool. Designed for security professionals, network administrators, and developers who need reliable network discovery and security auditing capabilities.

## 🚀 Key Features

- **🛡️ Type Safety**: Comprehensive type hints with enhanced error handling
- **⚡ Performance**: Asynchronous scanning with generator-based processing
- **📊 Multiple Output Formats**: CSV export and raw XML access
- **🔍 Comprehensive Analysis**: OS detection, service enumeration, and script execution
- **🔄 Flexible Scanning**: Synchronous, asynchronous, and yield-based scan modes
- **📈 Production Ready**: Robust error handling and logging for enterprise use

## 📦 Installation

### Prerequisites

**System Requirements:**
- Python 3.8 or higher
- Nmap 7.0+ installed on your system

### Install nust-nmap

```bash
pip install nust-nmap
```

### Install Nmap

#### Ubuntu/Debian
```bash
sudo apt update && sudo apt install nmap
```

#### CentOS/RHEL/Fedora
```bash
sudo dnf install nmap  # Fedora
sudo yum install nmap  # CentOS/RHEL
```

#### macOS
```bash
brew install nmap
```

#### Windows
Download and install from [nmap.org/download.html](https://nmap.org/download.html)

## 🔧 Quick Start

### Basic Network Scanning

```python
import nmap

# Initialize scanner
scanner = nmap.PortScanner()

# Perform basic host discovery
result = scanner.scan('192.168.1.0/24', '22,80,443,8080')

# Analyze results
for host in scanner.all_hosts():
    if scanner[host].state() == 'up':
        print(f"🟢 {host} ({scanner[host].hostname()}) - {scanner[host].state()}")
        
        for protocol in scanner[host].all_protocols():
            ports = scanner[host][protocol].keys()
            for port in sorted(ports):
                state = scanner[host][protocol][port]['state']
                service = scanner[host][protocol][port]['name']
                print(f"   Port {port}/{protocol}: {state} ({service})")
```

### Service Version Detection

```python
# Comprehensive service and version detection
scanner.scan('target.example.com', '1-1000', '-sV -sC -O')

for host in scanner.all_hosts():
    print(f"\n=== {host} ===")
    for port in scanner[host]['tcp']:
        service_info = scanner[host]['tcp'][port]
        print(f"Port {port}: {service_info['state']} "
              f"({service_info['name']} {service_info.get('version', '')})")
```

## 📖 Comprehensive Usage Guide

### Advanced Scanning Techniques

#### Stealth Scanning
```python
# SYN stealth scan with timing optimization
scanner.scan('target-network.com', '1-65535', '-sS -T4 --min-rate 1000')
```

#### Service and OS Detection
```python
# Comprehensive reconnaissance
scanner.scan('target.com', arguments='-sV -sC -O -A --script vuln')
```

#### Custom Nmap Scripts
```python
# Execute specific NSE scripts
scanner.scan('web-server.com', '80,443', '--script http-title,http-headers,ssl-cert')
```

### Asynchronous Scanning for Performance

```python
import time
import threading

class NetworkScanner:
    def __init__(self):
        self.results = []
        self.scan_complete = threading.Event()
    
    def scan_callback(self, host, scan_result):
        """Callback function for async scan results"""
        if scan_result:
            self.results.append((host, scan_result))
            print(f"✅ Completed scan for {host}")
        else:
            print(f"❌ Failed to scan {host}")
    
    def scan_network_async(self, network, ports):
        """Perform asynchronous network scan"""
        scanner = nmap.PortScannerAsync()
        
        scanner.scan(
            hosts=network,
            ports=ports,
            arguments='-sS -sV',
            callback=self.scan_callback
        )
        
        # Monitor scan progress
        while scanner.still_scanning():
            print(f"⏳ Scanning in progress... ({len(self.results)} hosts completed)")
            time.sleep(2)
        
        print(f"🎉 Network scan completed! Found {len(self.results)} responsive hosts")
        return self.results

# Usage
network_scanner = NetworkScanner()
results = network_scanner.scan_network_async('192.168.1.0/24', '22,80,443,8080')
```

### Generator-Based Processing

```python
def process_large_network(network_range, ports):
    """Efficiently process large network ranges"""
    scanner = nmap.PortScannerYield()
    
    active_hosts = []
    
    for host, result in scanner.scan(network_range, ports=ports, arguments='-sS'):
        if result and result['nmap']['scanstats']['uphosts'] != '0':
            active_hosts.append(host)
            print(f"📡 Active host discovered: {host}")
            
            # Process immediately to save memory
            yield host, result
    
    print(f"🔍 Discovery complete: {len(active_hosts)} active hosts found")

# Process enterprise network efficiently
for host, data in process_large_network('10.0.0.0/16', '22,80,443'):
    # Handle each host as discovered
    pass
```

### Data Export and Analysis

```python
import csv
from datetime import datetime

def export_scan_results(scanner, filename=None):
    """Export scan results to multiple formats"""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nmap_scan_{timestamp}"
    
    # Export to CSV
    csv_data = scanner.csv()
    with open(f"{filename}.csv", 'w', newline='') as f:
        f.write(csv_data)
    
    # Export raw XML
    xml_data = scanner.get_nmap_last_output()
    with open(f"{filename}.xml", 'w') as f:
        f.write(xml_data)
    
    print(f"📄 Results exported:")
    print(f"   CSV: {filename}.csv")
    print(f"   XML: {filename}.xml")
    
    return filename

# Usage
scanner.scan('192.168.1.0/24', '22,80,443,8080', '-sV')
export_scan_results(scanner, "network_audit_2024")
```

## 🔧 API Reference

### Core Classes

#### `PortScanner`
Primary synchronous scanning interface.

```python
scanner = nmap.PortScanner()
```

**Key Methods:**
- `scan(hosts, ports=None, arguments='-sV', sudo=False, timeout=0)` - Execute scan
- `listscan(hosts)` - Host discovery without port scanning
- `all_hosts()` - Retrieve all discovered hosts
- `has_host(host)` - Check if host exists in results
- `csv()` - Export results as CSV
- `get_nmap_last_output()` - Get raw XML output

#### `PortScannerAsync`
High-performance asynchronous scanning.

```python
async_scanner = nmap.PortScannerAsync()
async_scanner.scan(hosts, ports, arguments, callback)
```

#### `PortScannerYield`
Memory-efficient generator-based scanning.

```python
yield_scanner = nmap.PortScannerYield()
for host, result in yield_scanner.scan(hosts, ports):
    process_host(host, result)
```

### Host Data Access

```python
# Access host information
host = scanner['192.168.1.1']

# Host properties
host.hostname()              # DNS hostname
host.state()                # Host state (up/down)
host.all_protocols()        # Available protocols
host.all_tcp()              # TCP ports
host.all_udp()              # UDP ports

# Port-specific data
host.has_tcp(80)            # Check TCP port existence
port_info = host.tcp(80)    # Get port details
```

## 🛡️ Security Best Practices

### Ethical Scanning Guidelines

```python
import ipaddress

def validate_scan_target(target):
    """Validate scan targets against ethical guidelines"""
    
    # Define restricted networks
    restricted_networks = [
        ipaddress.ip_network('169.254.0.0/16'),  # Link-local
        ipaddress.ip_network('224.0.0.0/4'),    # Multicast
        ipaddress.ip_network('127.0.0.0/8'),    # Loopback (allow for testing)
    ]
    
    try:
        target_network = ipaddress.ip_network(target, strict=False)
        
        for restricted in restricted_networks:
            if target_network.overlaps(restricted) and not target.startswith('127.'):
                raise ValueError(f"Scanning {target} is not recommended")
                
    except ValueError as e:
        print(f"⚠️  Target validation warning: {e}")
        return False
    
    return True

# Always validate targets
if validate_scan_target('192.168.1.0/24'):
    scanner.scan('192.168.1.0/24', '22,80,443')
```

### Error Handling and Resilience

```python
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def safe_scan_context():
    """Context manager for safe scanning with cleanup"""
    scanner = None
    try:
        scanner = nmap.PortScanner()
        yield scanner
    except nmap.PortScannerError as e:
        logger.error(f"Scan error: {e}")
        raise
    except nmap.PortScannerTimeout as e:
        logger.warning(f"Scan timeout: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        if scanner:
            logger.info("Scan context cleanup completed")

# Robust scanning implementation
def robust_network_scan(network, ports, max_retries=3):
    """Perform network scan with retry logic"""
    
    for attempt in range(max_retries):
        try:
            with safe_scan_context() as scanner:
                result = scanner.scan(network, ports, arguments='-sS -T3')
                return scanner, result
                
        except nmap.PortScannerTimeout:
            if attempt < max_retries - 1:
                logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                continue
            raise
        except nmap.PortScannerError as e:
            logger.error(f"Scan failed: {e}")
            if "permission" in str(e).lower():
                logger.info("Try running with sudo for raw socket access")
            raise

# Usage
try:
    scanner, results = robust_network_scan('192.168.1.0/24', '22,80,443')
    logger.info(f"Successfully scanned {len(scanner.all_hosts())} hosts")
except Exception as e:
    logger.error(f"Network scan failed: {e}")
```

## 📊 Common Scan Patterns

| Scan Type | Command | Use Case |
|-----------|---------|----------|
| **Host Discovery** | `-sn` | Network reconnaissance |
| **Stealth Scan** | `-sS` | Firewall evasion |
| **Version Detection** | `-sV` | Service enumeration |
| **OS Detection** | `-O` | Operating system fingerprinting |
| **Aggressive Scan** | `-A` | Comprehensive analysis |
| **Script Scan** | `--script <category>` | Vulnerability assessment |
| **UDP Scan** | `-sU` | UDP service discovery |
| **Fast Scan** | `-T4 --min-rate 1000` | Time-sensitive scanning |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/codeNinja62/nust-nmap.git
cd nust-nmap

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Sameer Ahmed**
- Email: [sameer.cs@proton.me](mailto:sameer.cs@proton.me)
- GitHub: [@codeNinja62](https://github.com/codeNinja62)

## 🙏 Acknowledgments

- Built upon the robust [Nmap Security Scanner](https://nmap.org/)
- Inspired by the original python-nmap library
- Special thanks to the cybersecurity community for feedback and contributions

## 🔗 Links

- [📦 PyPI Package](https://pypi.org/project/nust-nmap/)
- [📚 Documentation](https://github.com/codeNinja62/nust-nmap/wiki)
- [🐛 Issue Tracker](https://github.com/codeNinja62/nust-nmap/issues)
- [🌐 Nmap Official Site](https://nmap.org/)

## ⚠️ Legal Disclaimer

**IMPORTANT: This tool is designed for authorized security testing and network administration only.**

- ✅ **Authorized Use**: Own networks, approved penetration testing, security research
- ❌ **Prohibited Use**: Unauthorized scanning, malicious activities, illegal reconnaissance

**Users are solely responsible for compliance with applicable laws and regulations. Always obtain explicit permission before scanning networks you do not own or administer.**

---

*"Know your network, secure your future."* 🛡️