"""
example.py - Demonstrates usage of python-nmap with enhanced coding standards.

Author: Alexandre Norman - norman@xael.org
Contributor: Steve 'Ashcrow' Milner - steve@gnulinux.net

License: GPL v3 or any later version

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
#!/usr/bin/env python3

import os
import sys
from typing import Any, Dict, Optional

import nmap  # import nmap.py module


def main() -> None:
    """Main function demonstrating python-nmap usage."""
    try:
        nm = nmap.PortScanner()
    except nmap.PortScannerError:
        print("Nmap not found", sys.exc_info()[0])
        sys.exit(1)
    except Exception:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)

    # Basic scan
    nm.scan("127.0.0.1", "22-443")
    print(f"Command line: {nm.command_line()}")
    print(f"Scan info: {nm.scaninfo()}")
    print(f"All hosts: {nm.all_hosts()}")

    host = "127.0.0.1"
    if host in nm.all_hosts():
        print(f"Hostname: {nm[host].hostname()}")
        print(f"Hostnames: {nm[host].hostnames()}")
        print(f"State: {nm[host].state()}")
        print(f"Protocols: {nm[host].all_protocols()}")
        if "tcp" in nm[host]:
            print(f"TCP ports: {list(nm[host]['tcp'].keys())}")
        print(f"All TCP ports: {nm[host].all_tcp()}")
        print(f"All UDP ports: {nm[host].all_udp()}")
        print(f"All IP ports: {nm[host].all_ip()}")
        print(f"All SCTP ports: {nm[host].all_sctp()}")
        if nm[host].has_tcp(22):
            print(f"TCP 22 info: {nm[host]['tcp'][22]}")
            print(f"TCP 22 info (method): {nm[host].tcp(22)}")
            print(f"TCP 22 state: {nm[host]['tcp'][22]['state']}")

    # More useful example: print all hosts and their ports
    for host in nm.all_hosts():
        print("----------------------------------------------------")
        print(f"Host: {host} ({nm[host].hostname()})")
        print(f"State: {nm[host].state()}")
        for proto in nm[host].all_protocols():
            print("----------")
            print(f"Protocol: {proto}")
            lport = list(nm[host][proto].keys())
            lport.sort()
            for port in lport:
                print(f"Port: {port}\tState: {nm[host][proto][port]}")

    print("----------------------------------------------------")
    print("CSV output:")
    print(nm.csv())

    print("----------------------------------------------------")
    print("Ping sweep example:")
    nm.scan(hosts="192.168.0.0/24", arguments="-n -sP -PE -PA21,23,80,3389")
    hosts_list = [(x, nm[x]["status"]["state"]) for x in nm.all_hosts()]
    for host, status in hosts_list:
        print(f"{host}: {status}")

    print("----------------------------------------------------")
    print("Asynchronous scan example:")

    def callback_result(host: str, scan_result: Optional[Dict[str, Any]]) -> None:
        """Callback function for async scan."""
        print("------------------")
        print(host, scan_result)

    nma = nmap.PortScannerAsync()
    nma.scan(hosts="192.168.0.0/30", arguments="-sP", callback=callback_result)

    while nma.still_scanning():
        print("Waiting ...")
        nma.wait(2)

    # OS detection (requires root)
    if hasattr(os, "getuid") and os.getuid() == 0:
        print("----------------------------------------------------")
        print("OS detection example:")
        nm.scan("127.0.0.1", arguments="-O")
        if "osmatch" in nm["127.0.0.1"]:
            for osmatch in nm["127.0.0.1"]["osmatch"]:
                print(f"OsMatch.name: {osmatch['name']}")
                print(f"OsMatch.accuracy: {osmatch['accuracy']}")
                print(f"OsMatch.line: {osmatch['line']}\n")
                if "osclass" in osmatch:
                    for osclass in osmatch["osclass"]:
                        print(f"OsClass.type: {osclass['type']}")
                        print(f"OsClass.vendor: {osclass['vendor']}")
                        print(f"OsClass.osfamily: {osclass['osfamily']}")
                        print(f"OsClass.osgen: {osclass['osgen']}")
                        print(f"OsClass.accuracy: {osclass['accuracy']}\n")
        if "fingerprint" in nm["127.0.0.1"]:
            print(f"Fingerprint: {nm['127.0.0.1']['fingerprint']}")
        print("Scanning localnet for MAC vendors:")
        nm.scan("192.168.0.0/24", arguments="-O")
        for h in nm.all_hosts():
            print(h)
            if "mac" in nm[h]["addresses"]:
                print(nm[h]["addresses"], nm[h]["vendor"])

    print("----------------------------------------------------")
    print("Read output from XML file:")
    try:
        with open("./nmap_output.xml") as fd:
            content = fd.read()
            nm.analyse_nmap_xml_scan(content)
            print(nm.csv())
    except FileNotFoundError:
        print("nmap_output.xml not found, skipping XML read example.")

    print("----------------------------------------------------")
    print("Progressive scan with generator:")
    nmy = nmap.PortScannerYield()
    for progressive_result in nmy.scan("127.0.0.1/24", "22-25"):
        print(progressive_result)

    print("----------------------------------------------------")
    print("Scan with timeout example:")
    nm = nmap.PortScanner()
    nm.scan("127.0.0.1", "22-40043", timeout=1)


if __name__ == "__main__":
    main()
