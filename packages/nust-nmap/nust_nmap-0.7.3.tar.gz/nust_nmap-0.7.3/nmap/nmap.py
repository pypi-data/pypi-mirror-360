"""
nmap.py - version and date, see below

Source code : https://github.com/codeNinja62/nust-nmap

Author :

* Alexandre Norman - norman at xael.org

Contributors:

* Sameer Ahmed - sameer.cs@proton.me
* Steve 'Ashcrow' Milner - steve at gnulinux.net
* Brian Bustin - brian at bustin.us
* old.schepperhand
* Johan Lundberg
* Thomas D. maaaaz
* Robert Bost
* David Peltier
* Ed Jones


Licence: GPL v3 or any later version for python-nmap


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


**************
IMPORTANT NOTE
**************

The Nmap Security Scanner used by python-nmap is distributed
under it's own licence that you can find at https://svn.nmap.org/nmap/COPYING

Any redistribution of python-nmap along with the Nmap Security Scanner
must conform to the Nmap Security Scanner licence

"""
import csv
import io
import logging
import os
import re
import shlex
import subprocess
import sys
import threading
import time
from multiprocessing import Process
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    TextIO,
    Tuple,
    Union,
)
from xml.etree import ElementTree as ET

__author__ = "Alexandre Norman (norman@xael.org)"
__version__ = "0.7.3"
__last_modification__ = "2025.07.07"


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


# Performance monitoring and caching support
ENABLE_PERFORMANCE_MONITORING = False
_scan_cache: Dict[str, Dict[str, Any]] = {}
_cache_max_age = 300  # 5 minutes default cache age

# Thread safety
_scan_lock = threading.Lock()


def enable_performance_monitoring(enabled: bool = True) -> None:
    """
    Enable or disable performance monitoring for scan operations.

    Args:
        enabled: Whether to enable performance monitoring
    """
    global ENABLE_PERFORMANCE_MONITORING
    ENABLE_PERFORMANCE_MONITORING = enabled
    if enabled:
        logger.info("Performance monitoring enabled")


def set_cache_max_age(seconds: int) -> None:
    """
    Set the maximum age for cached scan results.

    Args:
        seconds: Maximum age in seconds for cached results
    """
    global _cache_max_age
    if seconds < 0:
        raise ValueError("Cache max age must be non-negative")
    _cache_max_age = seconds
    logger.debug(f"Cache max age set to {seconds} seconds")


def clear_scan_cache() -> None:
    """Clear all cached scan results."""
    global _scan_cache
    with _scan_lock:
        _scan_cache.clear()
    logger.debug("Scan cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the scan cache.

    Returns:
        Dictionary containing cache statistics
    """
    with _scan_lock:
        return {
            "entries": len(_scan_cache),
            "max_age_seconds": _cache_max_age,
            "performance_monitoring": ENABLE_PERFORMANCE_MONITORING,
        }


############################################################################


class PortScanner:
    """
    PortScanner class allows to use nmap from python with enhanced error handling
    and type safety.

    This class provides a Python interface to the nmap network scanning tool,
    offering both synchronous scanning capabilities and comprehensive result parsing.

    Attributes:
        _nmap_path: Path to the nmap executable
        _scan_result: Dictionary containing the last scan results
        _nmap_version_number: Major version number of nmap
        _nmap_subversion_number: Minor version number of nmap
        _nmap_last_output: Raw output from the last nmap execution
    """

    def __init__(
        self,
        nmap_search_path: Tuple[str, ...] = (
            "nmap",
            "/usr/bin/nmap",
            "/usr/local/bin/nmap",
            "/sw/bin/nmap",
            "/opt/local/bin/nmap",
        ),
    ) -> None:
        """
        Initialize PortScanner module with enhanced error handling and type safety.

        * Detects nmap on the system and determines nmap version
        * Raises PortScannerError exception if nmap is not found in the path
        * Validates nmap installation and version compatibility

        Args:
            nmap_search_path: Tuple of strings where to search for nmap executable.
                            Change this if you want to use a specific version of nmap.

        Raises:
            PortScannerError: If nmap is not found in any of the search paths
            PortScannerError: If nmap version cannot be determined

        Returns:
            None
        """
        # Initialize instance attributes with proper types
        self._nmap_path: str = ""
        self._scan_result: Dict[str, Any] = {}
        self._nmap_version_number: int = 0
        self._nmap_subversion_number: int = 0
        self._nmap_last_output: str = ""
        self.__process: Optional[subprocess.Popen[bytes]] = None

        # Track if nmap was found and validated
        is_nmap_found: bool = False

        # Compiled regex for efficiency - used to detect nmap version
        version_regex = re.compile(
            r"Nmap version [0-9]*\.[0-9]*[^ ]* \( http(|s)://.* \)"
        )

        logger.debug(f"Searching for nmap in paths: {nmap_search_path}")

        # Search for nmap executable in the provided paths
        for nmap_path in nmap_search_path:
            try:
                logger.debug(f"Trying nmap path: {nmap_path}")

                # Platform-specific subprocess handling for better compatibility
                if (
                    sys.platform.startswith("freebsd")
                    or sys.platform.startswith("linux")
                    or sys.platform.startswith("darwin")
                ):
                    process = subprocess.Popen(
                        [nmap_path, "-V"],
                        bufsize=10000,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        close_fds=True,
                    )
                else:
                    # Windows and other platforms
                    process = subprocess.Popen(
                        [nmap_path, "-V"],
                        bufsize=10000,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

            except (OSError, FileNotFoundError) as e:
                logger.debug(f"Failed to execute nmap at {nmap_path}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error testing nmap at {nmap_path}: {e}")
                continue
            else:
                self._nmap_path = nmap_path
                logger.debug(f"Found nmap at: {nmap_path}")
                break
        else:
            # No nmap found in any of the search paths
            error_msg = f"nmap program was not found in path. Searched: {nmap_search_path}. PATH is: {os.getenv('PATH', 'Not set')}"
            logger.error(error_msg)
            raise PortScannerError(error_msg)

        # Get and parse nmap version information
        try:
            stdout, stderr = process.communicate(timeout=10)  # 10-second timeout
            self._nmap_last_output = stdout.decode("utf-8", errors="replace")

            if stderr:
                stderr_str = stderr.decode("utf-8", errors="replace")
                logger.warning(f"nmap stderr output: {stderr_str}")

        except subprocess.TimeoutExpired:
            process.kill()
            raise PortScannerError("Timeout while getting nmap version information")
        except Exception as e:
            raise PortScannerError(f"Error communicating with nmap process: {e}")

        # Parse version information from nmap output
        for line in self._nmap_last_output.split(os.linesep):
            if version_regex.match(line) is not None:
                is_nmap_found = True

                # Extract version numbers using more robust regex patterns
                version_match = re.search(r"(\d+)\.(\d+)", line)
                if version_match:
                    self._nmap_version_number = int(version_match.group(1))
                    self._nmap_subversion_number = int(version_match.group(2))
                    logger.info(
                        f"Detected nmap version: {self._nmap_version_number}.{self._nmap_subversion_number}"
                    )
                else:
                    logger.warning("Could not parse nmap version numbers from output")
                break

        if not is_nmap_found:
            error_msg = f"nmap program was found but version could not be determined. Output: {self._nmap_last_output}"
            logger.error(error_msg)
            raise PortScannerError(error_msg)

    def get_nmap_last_output(self) -> str:
        """
        Returns the last text output of nmap in raw text.

        This may be used for debugging purposes or for custom parsing
        of nmap output that is not handled by the standard parsing methods.

        Returns:
            String containing the last text output of nmap in raw text
        """
        return self._nmap_last_output

    def nmap_version(self) -> Tuple[int, int]:
        """
        Returns nmap version if detected, or (0, 0) if unknown.

        This method provides access to the detected nmap version information
        which can be useful for feature compatibility checks.

        Returns:
            Tuple containing (nmap_version_number, nmap_subversion_number)
        """
        return (self._nmap_version_number, self._nmap_subversion_number)

    def listscan(self, hosts: str = "127.0.0.1") -> List[str]:
        """
        Do not scan but interpret target hosts and return a list of hosts.

        This method uses nmap's list scan (-sL) functionality to resolve
        and enumerate hosts without actually scanning them.

        Args:
            hosts: String for hosts as nmap uses it (e.g., 'scanme.nmap.org'
                  or '198.116.0-255.1-127' or '216.163.128.20/20')

        Returns:
            List of strings representing the discovered hosts

        Raises:
            AssertionError: If hosts parameter is not a string
        """
        if not isinstance(hosts, str):
            raise TypeError(
                f"Wrong type for [hosts], should be a string [was {type(hosts)}]"
            )

        output = self.scan(hosts, arguments="-sL")

        # Test if host was IPv6
        if (
            "scaninfo" in output["nmap"]
            and "error" in output["nmap"]["scaninfo"]
            and len(output["nmap"]["scaninfo"]["error"]) > 0
            and "looks like an IPv6 target specification"
            in output["nmap"]["scaninfo"]["error"][0]
        ):
            self.scan(hosts, arguments="-sL -6")

        return self.all_hosts()

    def scan(
        self,
        hosts: str = "127.0.0.1",
        ports: Optional[str] = None,
        arguments: str = "-sV",
        sudo: bool = False,
        timeout: int = 0,
    ) -> Dict[str, Any]:
        """
        Scan given hosts with enhanced error handling and type safety.

        May raise PortScannerError exception if nmap output was not xml

        Test existence of the following key to know if something went wrong:
        ['nmap']['scaninfo']['error']. If not present, everything was ok.

        Args:
            hosts: String for hosts as nmap uses it (e.g., 'scanme.nmap.org'
                  or '198.116.0-255.1-127' or '216.163.128.20/20')
            ports: String for ports as nmap uses it (e.g., '22,53,110,143-4564')
            arguments: String of arguments for nmap (e.g., '-sU -sX -sC')
            sudo: Launch nmap with sudo if True
            timeout: If > 0, will terminate scan after timeout seconds,
                    otherwise will wait indefinitely

        Returns:
            Dictionary containing the scan results

        Raises:
            TypeError: If argument types are incorrect
            PortScannerError: If nmap execution fails
            PortScannerTimeout: If scan times out
        """
        # Enhanced type checking with better error messages
        if not isinstance(hosts, str):
            raise TypeError(
                f"Wrong type for [hosts], should be a string [was {type(hosts)}]"
            )

        if ports is not None and not isinstance(ports, str):
            raise TypeError(
                f"Wrong type for [ports], should be a string or None [was {type(ports)}]"
            )

        if not isinstance(arguments, str):
            raise TypeError(
                f"Wrong type for [arguments], should be a string [was {type(arguments)}]"
            )

        if not isinstance(sudo, bool):
            raise TypeError(
                f"Wrong type for [sudo], should be a boolean [was {type(sudo)}]"
            )

        if not isinstance(timeout, int):
            raise TypeError(
                f"Wrong type for [timeout], should be an integer [was {type(timeout)}]"
            )

        # Validate that output redirection is not used in arguments
        for redirecting_output in ["-oX", "-oA"]:
            if redirecting_output in arguments:
                raise ValueError(
                    "XML output can't be redirected from command line.\n"
                    "You can access it after a scan using: nmap.get_nmap_last_output()"
                )

        # Parse arguments safely
        try:
            h_args = shlex.split(hosts)
            f_args = shlex.split(arguments)
        except ValueError as e:
            raise PortScannerError(f"Error parsing arguments: {e}")

        # Build command arguments
        args = [self._nmap_path, "-oX", "-"] + h_args
        if ports is not None:
            args.extend(["-p", ports])
        args.extend(f_args)

        if sudo:
            args = ["sudo"] + args

        logger.debug(f"Executing nmap command: {' '.join(args)}")

        # Execute nmap with proper error handling
        try:
            p = subprocess.Popen(
                args,
                bufsize=100000,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (OSError, FileNotFoundError) as e:
            raise PortScannerError(f"Error executing nmap: {e}")

        # Handle timeout and get output
        try:
            if timeout == 0:
                stdout, nmap_err = p.communicate()
            else:
                stdout, nmap_err = p.communicate(timeout=timeout)

            # Properly decode bytes to string
            self._nmap_last_output = stdout.decode("utf-8", errors="replace")
            nmap_err_str = nmap_err.decode("utf-8", errors="replace")

        except subprocess.TimeoutExpired:
            p.kill()
            raise PortScannerTimeout("Timeout from nmap process")
        except Exception as e:
            raise PortScannerError(f"Error communicating with nmap: {e}")

        # Enhanced error and warning processing
        nmap_err_keep_trace: List[str] = []
        nmap_warn_keep_trace: List[str] = []

        if nmap_err_str:
            warning_regex = re.compile(r"^Warning: .*", re.IGNORECASE)
            for line in nmap_err_str.split(os.linesep):
                line = line.strip()
                if line:
                    if warning_regex.match(line):
                        nmap_warn_keep_trace.append(line)
                        logger.warning(f"nmap warning: {line}")
                    else:
                        nmap_err_keep_trace.append(line)
                        logger.error(f"nmap error: {line}")

        return self.analyse_nmap_xml_scan(
            nmap_xml_output=self._nmap_last_output,
            nmap_err=nmap_err_str,
            nmap_err_keep_trace=nmap_err_keep_trace,
            nmap_warn_keep_trace=nmap_warn_keep_trace,
        )

    def analyse_nmap_xml_scan(
        self,
        nmap_xml_output: Optional[str] = None,
        nmap_err: str = "",
        nmap_err_keep_trace: Optional[List[str]] = None,
        nmap_warn_keep_trace: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyses NMAP XML scan output with enhanced error handling and null safety.

        May raise PortScannerError exception if nmap output was not valid XML.

        Test existence of the following key to know if something went wrong:
        ['nmap']['scaninfo']['error']. If not present, everything was OK.

        Args:
            nmap_xml_output: XML string to analyse
            nmap_err: Error output from nmap
            nmap_err_keep_trace: List of error messages to preserve
            nmap_warn_keep_trace: List of warning messages to preserve

        Returns:
            Dictionary containing the parsed scan results

        Raises:
            PortScannerError: If XML parsing fails or nmap reported errors
        """
        # Set defaults for mutable arguments
        if nmap_err_keep_trace is None:
            nmap_err_keep_trace = []
        if nmap_warn_keep_trace is None:
            nmap_warn_keep_trace = []

        if nmap_xml_output is not None:
            self._nmap_last_output = nmap_xml_output

        scan_result: Dict[str, Any] = {}

        # Parse XML with enhanced error handling
        try:
            dom = ET.fromstring(self._nmap_last_output)
        except ET.ParseError as e:
            error_msg = f"Error parsing nmap XML output: {e}"
            if nmap_err:
                error_msg += f". nmap stderr: {nmap_err}"
            logger.error(error_msg)
            raise PortScannerError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error parsing nmap output: {e}"
            logger.error(error_msg)
            if nmap_err:
                raise PortScannerError(nmap_err)
            else:
                raise PortScannerError(error_msg)

        # Initialize scan result structure with null-safe element access
        def safe_get_element_text(
            element: Optional[ET.Element], attr: str, default: str = ""
        ) -> str:
            """Safely get attribute from XML element, returning default if None."""
            if element is not None:
                return element.get(attr, default)
            return default

        def safe_find_element(parent: ET.Element, path: str) -> Optional[ET.Element]:
            """Safely find element, with logging if not found."""
            element = parent.find(path)
            if element is None:
                logger.warning(f"XML element not found: {path}")
            return element

        # Build scan stats with null-safe access
        finished_element = safe_find_element(dom, "runstats/finished")
        hosts_element = safe_find_element(dom, "runstats/hosts")

        scan_result["nmap"] = {
            "command_line": safe_get_element_text(dom, "args"),
            "scaninfo": {},
            "scanstats": {
                "timestr": safe_get_element_text(finished_element, "timestr"),
                "elapsed": safe_get_element_text(finished_element, "elapsed"),
                "uphosts": safe_get_element_text(hosts_element, "up"),
                "downhosts": safe_get_element_text(hosts_element, "down"),
                "totalhosts": safe_get_element_text(hosts_element, "total"),
            },
        }

        # Add error and warning information if present
        if len(nmap_err_keep_trace) > 0:
            scan_result["nmap"]["scaninfo"]["error"] = nmap_err_keep_trace

        if len(nmap_warn_keep_trace) > 0:
            scan_result["nmap"]["scaninfo"]["warning"] = nmap_warn_keep_trace

        # Parse scan info
        for dsci in dom.findall("scaninfo"):
            protocol = dsci.get("protocol", "unknown")
            scan_result["nmap"]["scaninfo"][protocol] = {
                "method": dsci.get("type", ""),
                "services": dsci.get("services", ""),
            }

        scan_result["scan"] = {}

        # Parse host information with enhanced null safety
        for dhost in dom.findall("host"):
            # Extract host addresses and vendor information
            host: Optional[str] = None
            address_block: Dict[str, str] = {}
            vendor_block: Dict[str, str] = {}

            for address in dhost.findall("address"):
                addr_type = address.get("addrtype", "unknown")
                addr_value = address.get("addr", "")

                if addr_value:  # Only add if we have a valid address
                    address_block[addr_type] = addr_value
                    if addr_type == "ipv4":
                        host = addr_value
                    elif addr_type == "mac":
                        vendor = address.get("vendor")
                        if vendor:
                            vendor_block[addr_value] = vendor

            # Fallback host identification if IPv4 not found
            if host is None and address_block:
                # Try to get any address as fallback
                first_address = dhost.find("address")
                if first_address is not None:
                    host = safe_get_element_text(first_address, "addr")

            if host is None:
                logger.warning("No valid host address found, skipping host")
                continue

            # Extract hostnames with null safety
            hostnames: List[Dict[str, str]] = []
            hostname_elements = dhost.findall("hostnames/hostname")
            if hostname_elements:
                for dhostname in hostname_elements:
                    hostname_info = {
                        "name": dhostname.get("name", ""),
                        "type": dhostname.get("type", ""),
                    }
                    hostnames.append(hostname_info)
            else:
                hostnames.append({"name": "", "type": ""})

            # Initialize host data structure
            scan_result["scan"][host] = PortScannerHostDict({"hostnames": hostnames})
            scan_result["scan"][host]["addresses"] = address_block
            scan_result["scan"][host]["vendor"] = vendor_block

            # Parse host status
            for dstatus in dhost.findall("status"):
                scan_result["scan"][host]["status"] = {
                    "state": dstatus.get("state", "unknown"),
                    "reason": dstatus.get("reason", ""),
                }

            # Parse uptime information
            for duptime in dhost.findall("uptime"):
                scan_result["scan"][host]["uptime"] = {
                    "seconds": duptime.get("seconds", "0"),
                    "lastboot": duptime.get("lastboot", ""),
                }

            # Parse port information with enhanced null safety
            for dport in dhost.findall("ports/port"):
                # Get protocol and port with null checks
                protocol = dport.get("protocol")
                port_str = dport.get("portid")

                if not protocol or not port_str:
                    logger.warning(
                        f"Invalid port data: protocol={protocol}, port={port_str}"
                    )
                    continue

                try:
                    port = int(port_str)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid port number: {port_str}")
                    continue

                # Get state information with null safety
                state_element = dport.find("state")
                if state_element is None:
                    logger.warning(f"No state element found for port {port}")
                    continue

                state = safe_get_element_text(state_element, "state", "unknown")
                reason = safe_get_element_text(state_element, "reason", "")

                # Extract service information
                name = product = version = extrainfo = conf = cpe = ""
                for dservice in dport.findall("service"):
                    name = dservice.get("name", "")
                    product = dservice.get("product", "")
                    version = dservice.get("version", "")
                    extrainfo = dservice.get("extrainfo", "")
                    conf = dservice.get("conf", "")

                    # Extract CPE information
                    for dcpe in dservice.findall("cpe"):
                        if dcpe.text:
                            cpe = dcpe.text

                # Initialize protocol section if needed
                if protocol not in scan_result["scan"][host]:
                    scan_result["scan"][host][protocol] = {}

                # Store port information
                scan_result["scan"][host][protocol][port] = {
                    "state": state,
                    "reason": reason,
                    "name": name,
                    "product": product,
                    "version": version,
                    "extrainfo": extrainfo,
                    "conf": conf,
                    "cpe": cpe,
                }

                # Extract script output
                for dscript in dport.findall("script"):
                    script_id = dscript.get("id", "")
                    script_out = dscript.get("output", "")

                    if script_id:  # Only add if we have a valid script id
                        if "script" not in scan_result["scan"][host][protocol][port]:
                            scan_result["scan"][host][protocol][port]["script"] = {}
                        scan_result["scan"][host][protocol][port]["script"][
                            script_id
                        ] = script_out

            # Parse host scripts with null safety
            for dhostscript in dhost.findall("hostscript"):
                for dscript in dhostscript.findall("script"):
                    script_id = dscript.get("id", "")
                    script_output = dscript.get("output", "")

                    if script_id:  # Only add if we have a valid script id
                        if "hostscript" not in scan_result["scan"][host]:
                            scan_result["scan"][host]["hostscript"] = []

                        scan_result["scan"][host]["hostscript"].append(
                            {"id": script_id, "output": script_output}
                        )

            # Parse OS detection information with enhanced null safety
            for dos in dhost.findall("os"):
                osmatch_list: List[Dict[str, Any]] = []
                portused_list: List[Dict[str, str]] = []

                # Parse ports used for OS detection
                for dportused in dos.findall("portused"):
                    port_info = {
                        "state": dportused.get("state", ""),
                        "proto": dportused.get("proto", ""),
                        "portid": dportused.get("portid", ""),
                    }
                    portused_list.append(port_info)

                if portused_list:
                    scan_result["scan"][host]["portused"] = portused_list

                # Parse OS match information
                for dosmatch in dos.findall("osmatch"):
                    osmatch_info = {
                        "name": dosmatch.get("name", ""),
                        "accuracy": dosmatch.get("accuracy", "0"),
                        "line": dosmatch.get("line", ""),
                        "osclass": [],
                    }

                    # Parse OS class information
                    for dosclass in dosmatch.findall("osclass"):
                        cpe_list: List[str] = []
                        for dcpe in dosclass.findall("cpe"):
                            if dcpe.text:
                                cpe_list.append(dcpe.text)

                        osclass_info = {
                            "type": dosclass.get("type", ""),
                            "vendor": dosclass.get("vendor", ""),
                            "osfamily": dosclass.get("osfamily", ""),
                            "osgen": dosclass.get("osgen", ""),
                            "accuracy": dosclass.get("accuracy", "0"),
                            "cpe": cpe_list,
                        }
                        osmatch_info["osclass"].append(osclass_info)

                    osmatch_list.append(osmatch_info)

                if osmatch_list:
                    scan_result["scan"][host]["osmatch"] = osmatch_list

            # Parse OS fingerprint information
            for dfingerprint in dhost.findall("osfingerprint"):
                fingerprint = dfingerprint.get("fingerprint", "")
                if fingerprint:
                    scan_result["scan"][host]["fingerprint"] = fingerprint

        # Store results and return
        self._scan_result = scan_result
        logger.debug(
            f"Scan analysis completed. Found {len(scan_result.get('scan', {}))} hosts"
        )
        return scan_result

    def __getitem__(self, host: str) -> "PortScannerHostDict":
        """
        Returns host scan details with type safety.

        Args:
            host: String representing the host IP or hostname

        Returns:
            PortScannerHostDict containing the host scan results

        Raises:
            TypeError: If host is not a string
            KeyError: If host is not found in scan results
        """
        if not isinstance(host, str):
            raise TypeError(
                f"Wrong type for [host], should be a string [was {type(host)}]"
            )

        if "scan" not in self._scan_result:
            raise KeyError("No scan results available. Run a scan first.")

        if host not in self._scan_result["scan"]:
            raise KeyError(f"Host '{host}' not found in scan results")

        return PortScannerHostDict(self._scan_result["scan"][host])

    def all_hosts(self) -> List[str]:
        """
        Returns a sorted list of all hosts from the last scan.

        Returns:
            List of strings representing the discovered hosts, sorted alphabetically
        """
        if "scan" not in self._scan_result:
            logger.warning("No scan results available")
            return []

        hosts: List[str] = list(self._scan_result["scan"].keys())
        hosts.sort()
        return hosts

    def command_line(self) -> str:
        """
        Returns the command line used for the last scan.

        Returns:
            String containing the nmap command line that was executed

        Raises:
            RuntimeError: If called before scanning
        """
        if "nmap" not in self._scan_result:
            raise RuntimeError("No scan results available. Run a scan first.")

        if "command_line" not in self._scan_result["nmap"]:
            raise RuntimeError("Command line information not available")

        return str(self._scan_result["nmap"]["command_line"])

    def scaninfo(self) -> Dict[str, Any]:
        """
        Returns scan information structure.

        Example return:
        {'tcp': {'services': '22', 'method': 'connect'}}

        Returns:
            Dictionary containing scan information organized by protocol

        Raises:
            RuntimeError: If called before scanning
        """
        if "nmap" not in self._scan_result:
            raise RuntimeError("No scan results available. Run a scan first.")

        if "scaninfo" not in self._scan_result["nmap"]:
            raise RuntimeError("Scan info not available")

        return dict(self._scan_result["nmap"]["scaninfo"])

    def scanstats(self) -> Dict[str, str]:
        """
        Returns scan statistics structure.

        Example return:
        {
            'uphosts': '3',
            'timestr': 'Thu Jun  3 21:45:07 2010',
            'downhosts': '253',
            'totalhosts': '256',
            'elapsed': '5.79'
        }

        Returns:
            Dictionary containing scan statistics

        Raises:
            RuntimeError: If called before scanning
        """
        if "nmap" not in self._scan_result:
            raise RuntimeError("No scan results available. Run a scan first.")

        if "scanstats" not in self._scan_result["nmap"]:
            raise RuntimeError("Scan stats not available")

        return dict(self._scan_result["nmap"]["scanstats"])

    def has_host(self, host: str) -> bool:
        """
        Returns True if host has scan results, False otherwise.

        Args:
            host: String representing the host IP or hostname to check

        Returns:
            Boolean indicating whether the host was found in scan results

        Raises:
            TypeError: If host is not a string
            RuntimeError: If called before scanning
        """
        if not isinstance(host, str):
            raise TypeError(
                f"Wrong type for [host], should be a string [was {type(host)}]"
            )

        if "scan" not in self._scan_result:
            raise RuntimeError("No scan results available. Run a scan first.")

        return host in self._scan_result["scan"]

    def csv(self) -> str:
        """
        Returns CSV output as text with enhanced formatting.

        Example output:
        host;hostname;hostname_type;protocol;port;name;state;product;extrainfo;reason;version;conf;cpe
        127.0.0.1;localhost;PTR;tcp;22;ssh;open;OpenSSH;protocol 2.0;syn-ack;5.9p1 Debian 5ubuntu1;10;cpe:/a:openbsd:openssh:5.9p1
        127.0.0.1;localhost;PTR;tcp;23;telnet;closed;;;conn-refused;;3;
        127.0.0.1;localhost;PTR;tcp;24;priv-mail;closed;;;conn-refused;;3;

        Returns:
            String containing CSV-formatted scan results

        Raises:
            RuntimeError: If called before scanning
        """
        if "scan" not in self._scan_result:
            raise RuntimeError("No scan results available. Run a scan first.")

        # Use StringIO for consistent string handling
        output_buffer = io.StringIO()
        csv_writer = csv.writer(output_buffer, delimiter=";")

        # Define CSV headers
        headers = [
            "host",
            "hostname",
            "hostname_type",
            "protocol",
            "port",
            "name",
            "state",
            "product",
            "extrainfo",
            "reason",
            "version",
            "conf",
            "cpe",
        ]
        csv_writer.writerow(headers)

        # Process each host
        for host in self.all_hosts():
            host_data = self[host]

            # Process each protocol for the host
            for protocol in host_data.all_protocols():
                if protocol not in [
                    "tcp",
                    "udp",
                    "ip",
                    "sctp",
                ]:  # Include all common protocols
                    continue

                # Get sorted list of ports
                ports = list(host_data[protocol].keys())
                ports.sort()

                # Process each port
                for port in ports:
                    port_info = host_data[protocol][port]

                    # Process each hostname or use empty if none
                    hostnames = host_data.hostnames()
                    if not hostnames:
                        hostnames = [{"name": "", "type": ""}]

                    for hostname_info in hostnames:
                        row = [
                            host,
                            hostname_info.get("name", ""),
                            hostname_info.get("type", ""),
                            protocol,
                            str(port),
                            port_info.get("name", ""),
                            port_info.get("state", ""),
                            port_info.get("product", ""),
                            port_info.get("extrainfo", ""),
                            port_info.get("reason", ""),
                            port_info.get("version", ""),
                            port_info.get("conf", ""),
                            port_info.get("cpe", ""),
                        ]
                        csv_writer.writerow(row)

        return output_buffer.getvalue()


############################################################################


def __scan_progressive__(
    scanner_instance: "PortScannerAsync",
    hosts: str,
    ports: Optional[str],
    arguments: str,
    callback: Optional[Callable[[str, Optional[Dict[str, Any]]], None]],
    sudo: bool,
    timeout: int,
) -> None:
    """
    Used by PortScannerAsync for progressive scanning with callback support.

    This function scans hosts progressively and calls the callback function
    for each completed host scan.

    Args:
        scanner_instance: The PortScannerAsync instance
        hosts: Host specification string
        ports: Port specification string
        arguments: nmap arguments
        callback: Callback function to call for each host
        sudo: Whether to use sudo
        timeout: Scan timeout
    """
    try:
        for host in scanner_instance._nm.listscan(hosts):
            try:
                scan_data = scanner_instance._nm.scan(
                    host, ports, arguments, sudo, timeout
                )
            except PortScannerError as e:
                logger.error(f"Error scanning host {host}: {e}")
                scan_data = None

            if callback is not None:
                try:
                    callback(host, scan_data)
                except Exception as e:
                    logger.error(f"Error in callback for host {host}: {e}")
    except Exception as e:
        logger.error(f"Error in progressive scan: {e}")


############################################################################


class PortScannerAsync:
    """
    PortScannerAsync allows to use nmap from python asynchronously.

    For each host scanned, callback is called with scan result for the host.
    This provides non-blocking scanning capabilities with real-time results.
    """

    def __init__(self) -> None:
        """
        Initialize the PortScannerAsync module.

        * Detects nmap on the system and nmap version
        * May raise PortScannerError exception if nmap is not found in the path
        """
        self._process: Optional[Process] = None
        self._nm: PortScanner = PortScanner()

    def __del__(self) -> None:
        """
        Cleanup when deleted - ensures proper process termination.
        """
        if self._process is not None:
            try:
                if self._process.is_alive():
                    self._process.terminate()
                    # Give process time to terminate gracefully
                    self._process.join(timeout=5)
                    if self._process.is_alive():
                        # Force kill if still alive
                        self._process.kill()
                        self._process.join()
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")
            finally:
                self._process = None

    def scan(
        self,
        hosts: str = "127.0.0.1",
        ports: Optional[str] = None,
        arguments: str = "-sV",
        callback: Optional[Callable[[str, Optional[Dict[str, Any]]], None]] = None,
        sudo: bool = False,
        timeout: int = 0,
    ) -> None:
        """
        Scan given hosts in a separate process and return host by host result using callback function.

        PortScannerError exceptions from standard nmap are caught and you won't know about them,
        but will get None as scan_data in the callback.

        Args:
            hosts: String for hosts as nmap uses it (e.g., 'scanme.nmap.org'
                  or '198.116.0-255.1-127' or '216.163.128.20/20')
            ports: String for ports as nmap uses it (e.g., '22,53,110,143-4564')
            arguments: String of arguments for nmap (e.g., '-sU -sX -sC')
            callback: Callback function which takes (host, scan_data) as arguments
            sudo: Launch nmap with sudo if True
            timeout: If > 0, will terminate scan after timeout seconds,
                    otherwise will wait indefinitely
        """
        # Enhanced type checking
        if not isinstance(hosts, str):
            raise TypeError(
                f"Wrong type for [hosts], should be a string [was {type(hosts)}]"
            )

        if ports is not None and not isinstance(ports, str):
            raise TypeError(
                f"Wrong type for [ports], should be a string or None [was {type(ports)}]"
            )

        if not isinstance(arguments, str):
            raise TypeError(
                f"Wrong type for [arguments], should be a string [was {type(arguments)}]"
            )

        if callback is not None and not callable(callback):
            raise TypeError(f"The [callback] {callback} should be callable or None.")

        # Validate that output redirection is not used in arguments
        for redirecting_output in ["-oX", "-oA"]:
            if redirecting_output in arguments:
                raise ValueError(
                    "XML output can't be redirected from command line.\n"
                    "You can access it after a scan using: nmap.get_nmap_last_output()"
                )

        # Start the scanning process
        self._process = Process(
            target=__scan_progressive__,
            args=(self, hosts, ports, arguments, callback, sudo, timeout),
        )
        self._process.daemon = True
        self._process.start()
        logger.debug(f"Started async scan process with PID: {self._process.pid}")

    def stop(self) -> None:
        """
        Stop the current scan process gracefully.
        """
        if self._process is not None and self._process.is_alive():
            logger.debug(f"Stopping scan process PID: {self._process.pid}")
            try:
                self._process.terminate()
                self._process.join(timeout=5)  # Wait up to 5 seconds
                if self._process.is_alive():
                    logger.warning("Process didn't terminate gracefully, forcing kill")
                    self._process.kill()
                    self._process.join()
            except Exception as e:
                logger.error(f"Error stopping scan process: {e}")

    def wait(self, timeout: Optional[int] = None) -> None:
        """
        Wait for the current scan process to finish, or timeout.

        Args:
            timeout: Wait timeout in seconds. If None, wait indefinitely.
        """
        if timeout is not None and not isinstance(timeout, int):
            raise TypeError(
                f"Wrong type for [timeout], should be an int or None [was {type(timeout)}]"
            )

        if self._process is not None:
            try:
                self._process.join(timeout)
            except Exception as e:
                logger.error(f"Error waiting for process: {e}")

    def still_scanning(self) -> bool:
        """
        Check if a scan is currently running.

        Returns:
            True if a scan is currently running, False otherwise
        """
        try:
            if self._process is not None:
                return self._process.is_alive()
            return False
        except Exception as e:
            logger.error(f"Error checking process status: {e}")
            return False


############################################################################


class PortScannerYield:
    """
    PortScannerYield allows to use nmap from python with a generator
    for each host scanned, yield is called with scan result for the host

    """

    def __init__(self) -> None:
        """
        Initialize the module.

        * Detects nmap on the system and nmap version
        * May raise PortScannerError exception if nmap is not found in the path
        """
        self._nm: PortScanner = PortScanner()

    def scan(
        self,
        hosts: str = "127.0.0.1",
        ports: Optional[str] = None,
        arguments: str = "-sV",
        sudo: bool = False,
        timeout: int = 0,
    ) -> Generator[Tuple[str, Optional[Dict[str, Any]]], None, None]:
        """
        Scan given hosts and yield results for each host.

        PortScannerError exceptions from standard nmap are caught and you won't know about them,
        but will get None as scan_data for that host.

        Args:
            hosts: String for hosts as nmap uses it (e.g., 'scanme.nmap.org'
                  or '198.116.0-255.1-127' or '216.163.128.20/20')
            ports: String for ports as nmap uses it (e.g., '22,53,110,143-4564')
            arguments: String of arguments for nmap (e.g., '-sU -sX -sC')
            sudo: Launch nmap with sudo if True
            timeout: If > 0, will terminate scan after timeout seconds,
                    otherwise will wait indefinitely

        Yields:
            Tuple containing (host, scan_data) for each scanned host
        """
        # Enhanced type checking
        if not isinstance(hosts, str):
            raise TypeError(
                f"Wrong type for [hosts], should be a string [was {type(hosts)}]"
            )

        if ports is not None and not isinstance(ports, str):
            raise TypeError(
                f"Wrong type for [ports], should be a string or None [was {type(ports)}]"
            )

        if not isinstance(arguments, str):
            raise TypeError(
                f"Wrong type for [arguments], should be a string [was {type(arguments)}]"
            )

        # Validate that output redirection is not used in arguments
        for redirecting_output in ["-oX", "-oA"]:
            if redirecting_output in arguments:
                raise ValueError(
                    "XML output can't be redirected from command line.\n"
                    "You can access it after a scan using: nmap.get_nmap_last_output()"
                )

        # Scan each host and yield results
        for host in self._nm.listscan(hosts):
            try:
                scan_data = self._nm.scan(host, ports, arguments, sudo, timeout)
                yield (host, scan_data)
            except PortScannerError as e:
                logger.error(f"Error scanning host {host}: {e}")
                yield (host, None)

    def stop(self) -> None:
        """
        Stop method for compatibility with PortScannerAsync interface.

        Note: This is a no-op for PortScannerYield as it uses synchronous scanning.
        """
        pass

    def wait(self, timeout: Optional[int] = None) -> None:
        """
        Wait method for compatibility with PortScannerAsync interface.

        Note: This is a no-op for PortScannerYield as it uses synchronous scanning.

        Args:
            timeout: Ignored for compatibility
        """
        pass

    def still_scanning(self) -> bool:
        """
        Check if scanning is in progress.

        Returns:
            False - PortScannerYield uses synchronous scanning
        """
        return False


############################################################################


class PortScannerHostDict(dict):
    """
    Special dictionnary class for storing and accessing host scan result

    """

    def hostnames(self) -> List[Dict[str, str]]:
        """
        :returns: list of hostnames

        """
        return self["hostnames"]

    def hostname(self) -> str:
        """
        For compatibility purpose...
        :returns: try to return the user record or the first hostname of the list hostnames

        """
        hostname = ""
        for h in self["hostnames"]:
            if h["type"] == "user":
                return h["name"]
        else:
            if len(self["hostnames"]) > 0 and "name" in self["hostnames"][0]:
                return self["hostnames"][0]["name"]
            else:
                return ""

        return hostname

    def state(self) -> str:
        """
        :returns: host state

        """
        return self["status"]["state"]

    def uptime(self) -> Dict[str, str]:
        """
        :returns: host state

        """
        return self["uptime"]

    def all_protocols(self) -> List[str]:
        """
        :returns: a list of all scanned protocols

        """

        def _proto_filter(x: str) -> bool:
            return x in ["ip", "tcp", "udp", "sctp"]

        lp = list(filter(_proto_filter, list(self.keys())))
        lp.sort()
        return lp

    def all_tcp(self) -> List[int]:
        """
        :returns: list of tcp ports

        """
        if "tcp" in list(self.keys()):
            ltcp = list(self["tcp"].keys())
            ltcp.sort()
            return ltcp
        return []

    def has_tcp(self, port: int) -> bool:
        """
        :param port: (int) tcp port
        :returns: True if tcp port has info, False otherwise

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"

        if "tcp" in list(self.keys()) and port in list(self["tcp"].keys()):
            return True
        return False

    def tcp(self, port: int) -> Dict[str, Any]:
        """
        :param port: (int) tcp port
        :returns: info for tcp port

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"
        return self["tcp"][port]

    def all_udp(self) -> List[int]:
        """
        :returns: list of udp ports

        """
        if "udp" in list(self.keys()):
            ludp = list(self["udp"].keys())
            ludp.sort()
            return ludp
        return []

    def has_udp(self, port: int) -> bool:
        """
        :param port: (int) udp port
        :returns: True if udp port has info, False otherwise

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"

        if "udp" in list(self.keys()) and "port" in list(self["udp"].keys()):
            return True
        return False

    def udp(self, port: int) -> Dict[str, Any]:
        """
        :param port: (int) udp port
        :returns: info for udp port

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"

        return self["udp"][port]

    def all_ip(self) -> List[int]:
        """
        :returns: list of ip ports

        """
        if "ip" in list(self.keys()):
            lip = list(self["ip"].keys())
            lip.sort()
            return lip
        return []

    def has_ip(self, port: int) -> bool:
        """
        :param port: (int) ip port
        :returns: True if ip port has info, False otherwise

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"

        if "ip" in list(self.keys()) and port in list(self["ip"].keys()):
            return True
        return False

    def ip(self, port: int) -> Dict[str, Any]:
        """
        :param port: (int) ip port
        :returns: info for ip port

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"

        return self["ip"][port]

    def all_sctp(self) -> List[int]:
        """
        :returns: list of sctp ports

        """
        if "sctp" in list(self.keys()):
            lsctp = list(self["sctp"].keys())
            lsctp.sort()
            return lsctp
        return []

    def has_sctp(self, port: int) -> bool:
        """
        :returns: True if sctp port has info, False otherwise

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"

        if "sctp" in list(self.keys()) and port in list(self["sctp"].keys()):
            return True
        return False

    def sctp(self, port: int) -> Dict[str, Any]:
        """
        :returns: info for sctp port

        """
        assert (
            type(port) is int
        ), f"Wrong type for [port], should be an int [was {type(port)}]"

        return self["sctp"][port]


############################################################################


class PortScannerError(Exception):
    """
    Exception error class for PortScanner class with enhanced error information.

    This exception is raised when nmap execution fails or when invalid
    parameters are provided to scanning methods.
    """

    def __init__(self, value: str) -> None:
        """
        Initialize the exception with error message.

        Args:
            value: Error message describing what went wrong
        """
        self.value = value
        super().__init__(value)

    def __str__(self) -> str:
        """Return string representation of the error."""
        return self.value

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return f"PortScannerError('{self.value}')"


class PortScannerTimeout(PortScannerError):
    """
    Exception raised when nmap scan times out.

    This is a specialized PortScannerError that indicates the scan
    operation exceeded the specified timeout limit.
    """

    def __init__(self, value: str = "Scan operation timed out") -> None:
        """
        Initialize timeout exception.

        Args:
            value: Timeout error message
        """
        super().__init__(value)

    def __repr__(self) -> str:
        """Return detailed representation of the timeout error."""
        return f"PortScannerTimeout('{self.value}')"


############################################################################


def __get_last_online_version() -> str:
    """
    Gets last python-nmap published version with enhanced error handling.

    WARNING: This function makes an HTTP connection to
    http://xael.org/pages/python-nmap/python-nmap_CURRENT_VERSION.txt

    Returns:
        String indicating the last published version (e.g., '0.4.3')

    Raises:
        PortScannerError: If unable to fetch version information
    """
    import http.client

    try:
        conn = http.client.HTTPConnection("xael.org", timeout=10)
        conn.request("GET", "/pages/python-nmap/python-nmap_CURRENT_VERSION.txt")
        response = conn.getresponse()

        if response.status == 200:
            online_version = response.read().decode("utf-8", errors="replace").strip()
            conn.close()
            return online_version
        else:
            conn.close()
            raise PortScannerError(
                f"HTTP error {response.status} when fetching version"
            )

    except Exception as e:
        raise PortScannerError(f"Error fetching online version: {e}")


############################################################################


def convert_nmap_output_to_encoding(
    value: Union[Dict[str, Any], List[Any], str], code: str = "ascii"
) -> Union[Dict[str, Any], List[Any], bytes]:
    """
    Change encoding for scan_result object from unicode to specified encoding.

    This function recursively processes dictionaries, lists, and strings to convert
    their encoding. Useful for legacy systems that require specific text encodings.

    Args:
        value: Scan result as dictionary, list, or string to convert
        code: Target encoding (default: "ascii")

    Returns:
        Converted scan result with new encoding

    Raises:
        UnicodeEncodeError: If string cannot be encoded to target encoding
    """
    if isinstance(value, dict):
        new_value: Dict[str, Any] = {}
        for k, v in value.items():
            if isinstance(v, (dict, PortScannerHostDict)):
                new_value[k] = convert_nmap_output_to_encoding(v, code)
            elif isinstance(v, list):
                new_value[k] = [convert_nmap_output_to_encoding(x, code) for x in v]
            elif isinstance(v, str):
                new_value[k] = v.encode(code, errors="replace")
            else:
                new_value[k] = v
        return new_value
    elif isinstance(value, list):
        return [convert_nmap_output_to_encoding(item, code) for item in value]
    elif isinstance(value, str):
        return value.encode(code, errors="replace")
    else:
        return value


# <EOF>######################################################################
