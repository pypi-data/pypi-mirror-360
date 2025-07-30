# python-nmap

[![PyPI latest](https://img.shields.io/pypi/v/python-nmap.svg?maxAge=360)](https://pypi.python.org/pypi/python-nmap)
[![PyPI Version](https://img.shields.io/pypi/pyversions/python-nmap.svg?maxAge=2592000)](https://pypi.python.org/pypi/python-nmap)
[![PyPI License](https://img.shields.io/pypi/l/python-nmap.svg?maxAge=2592000)](https://pypi.python.org/pypi/python-nmap)

**python-nmap** is a Python library for using the nmap port scanner. It allows you to easily manipulate nmap scan results and is a perfect tool for system administrators who want to automate scanning tasks and reports. It also supports nmap script outputs and asynchronous scanning.

## Features

- Run nmap scans from Python
- Parse and process nmap XML output
- Asynchronous scanning with callbacks
- Access scan results as Python objects
- Export results as CSV

## Installation

Install from PyPI:

```bash
pip install python-nmap
```

Or from source:

```bash
git clone https://github.com/codeNinja62/python-nmap
cd python-nmap
python setup.py install
```

## Usage

### Basic Example

```python
import nmap

nm = nmap.PortScanner()
nm.scan('127.0.0.1', '22-443')
print(nm.command_line())
print(nm.scaninfo())
print(nm.all_hosts())

host = '127.0.0.1'
if host in nm.all_hosts():
    print(nm[host].hostname())
    print(nm[host].state())
    print(nm[host].all_protocols())
    if 'tcp' in nm[host]:
        print(list(nm[host]['tcp'].keys()))
    print(nm[host].has_tcp(22))
    print(nm[host]['tcp'][22])
```

### Export to CSV

```python
print(nm.csv())
```

### Network Status

```python
nm.scan(hosts='192.168.1.0/24', arguments='-n -sP -PE -PA21,23,80,3389')
hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
for host, status in hosts_list:
    print(f"{host}:{status}")
```

### Asynchronous Scanning

```python
nma = nmap.PortScannerAsync()
def callback_result(host, scan_result):
    print('------------------')
    print(host, scan_result)

nma.scan(hosts='192.168.1.0/30', arguments='-sP', callback=callback_result)
while nma.still_scanning():
    print("Waiting ...")
    nma.wait(2)
```

### Progressive Scan

```python
nmy = nmap.PortScannerYield()
for progressive_result in nmy.scan('127.0.0.1/24', '22-25'):
    print(progressive_result)
```

### Scan with Timeout

```python
nm = nmap.PortScanner()
nm.scan('127.0.0.1', '22-40043', timeout=10)
```

## Contributors

Alexandre Norman
Sameer Ahmed
Steve 'Ashcrow' Milner
Brian Bustin
old.schepperhand
Johan Lundberg
Thomas D. maaaaz
Robert Bost
David Peltier
Ed Jones

## Homepage

[https://github.com/codeNinja62/python-nmap](https://github.com/codeNinja62/python-nmap)

## License

GPL v3 or any later version. See LICENSE for details.