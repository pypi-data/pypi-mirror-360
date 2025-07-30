"""
Enhanced python-nmap example demonstrating new features and best practices.

This example showcases the improved error handling, type safety, and
performance enhancements of the upgraded python-nmap library.
"""
#!/usr/bin/env python


import logging
from typing import Any, Dict, Optional

from nmap import PortScanner, PortScannerAsync, PortScannerError, PortScannerYield

# Configure logging to see enhanced debug information
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def example_basic_scan() -> None:
    """Demonstrate basic scanning with enhanced error handling."""
    nm = PortScanner()

    try:
        print(f"Nmap version: {nm.nmap_version()}")

        # Scan with timeout and enhanced error handling
        result = nm.scan("127.0.0.1", "22-443", timeout=30)

        print(f"Command executed: {nm.command_line()}")
        print(f"Scan info: {nm.scaninfo()}")
        print(f"Hosts discovered: {nm.all_hosts()}")

        for host in nm.all_hosts():
            print(f"Host: {host} ({nm[host].state()})")
            for protocol in nm[host].all_protocols():
                ports = nm[host][protocol].keys()
                for port in ports:
                    port_info = nm[host][protocol][port]
                    print(
                        f"  {protocol}/{port}: {port_info['state']} - {port_info['name']}"
                    )

    except PortScannerError as e:
        print(f"Scan error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_async_scan() -> None:
    """Demonstrate asynchronous scanning with callback."""

    def scan_callback(host: str, scan_data: Optional[Dict[str, Any]]) -> None:
        """Callback function for async scanning."""
        if scan_data:
            print(f"✓ Completed scan for {host}")
        else:
            print(f"✗ Failed to scan {host}")

    nm_async = PortScannerAsync()

    try:
        print("Starting async scan...")
        nm_async.scan("127.0.0.1", "80,443", callback=scan_callback)

        # Wait for completion
        nm_async.wait(timeout=60)
        print("Async scan completed")

    except Exception as e:
        print(f"Async scan error: {e}")
    finally:
        nm_async.stop()


def example_yield_scan() -> None:
    """Demonstrate generator-based scanning."""
    nm_yield = PortScannerYield()

    try:
        print("Starting yield-based scan...")
        for host, scan_data in nm_yield.scan("127.0.0.1", "22,80,443"):
            if scan_data:
                print(
                    f"Scanned {host}: {len(scan_data.get('scan', {}).get(host, {}))} protocols found"
                )
            else:
                print(f"Failed to scan {host}")

    except Exception as e:
        print(f"Yield scan error: {e}")


def example_csv_export() -> None:
    """Demonstrate enhanced CSV export functionality."""
    nm = PortScanner()

    try:
        nm.scan("127.0.0.1", "22,80,443")
        csv_output = nm.csv()

        print("CSV Export (first 5 lines):")
        lines = csv_output.split("\n")
        for line in lines[:5]:
            if line.strip():
                print(line)

    except Exception as e:
        print(f"CSV export error: {e}")


if __name__ == "__main__":
    print("=== Enhanced Python-Nmap Library Demo ===\n")

    print("1. Basic Scan Example:")
    example_basic_scan()
    print()

    print("2. Async Scan Example:")
    example_async_scan()
    print()

    print("3. Yield Scan Example:")
    example_yield_scan()
    print()

    print("4. CSV Export Example:")
    example_csv_export()
    print()

    print("Demo completed!")
