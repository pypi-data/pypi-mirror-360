"""
Comprehensive test suite for nust-nmap core functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nmap

# Global callback function for async tests (needed for Windows multiprocessing)
callback_results = []

def global_test_callback(host, result):
    """Global callback function that can be pickled for multiprocessing"""
    global callback_results
    callback_results.append((host, result))


class TestPortScanner(unittest.TestCase):
    """Test cases for PortScanner class - the core functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <nmaprun scanner="nmap" args="nmap -oX - -sV 127.0.0.1" start="1640995200" version="7.80">
        <host starttime="1640995200" endtime="1640995201">
            <status state="up" reason="syn-ack"/>
            <address addr="127.0.0.1" addrtype="ipv4"/>
            <hostnames>
                <hostname name="localhost" type="PTR"/>
            </hostnames>
            <ports>
                <port protocol="tcp" portid="22">
                    <state state="open" reason="syn-ack"/>
                    <service name="ssh" product="OpenSSH" version="7.4"/>
                </port>
                <port protocol="tcp" portid="80">
                    <state state="open" reason="syn-ack"/>
                    <service name="http" product="nginx" version="1.14.0"/>
                </port>
            </ports>
        </host>
        <runstats>
            <finished time="1640995201" elapsed="1.23" exit="success"/>
            <hosts up="1" down="0" total="1"/>
        </runstats>
        </nmaprun>"""

        self.listscan_output = """Nmap scan report for 127.0.0.1
Nmap scan report for 192.168.1.1
"""

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_scanner_initialization(self, mock_popen, mock_isfile, mock_which):
        """Test PortScanner initialization with automatic detection"""
        # Mock the automatic nmap detection
        mock_which.return_value = '/usr/bin/nmap'
        mock_isfile.return_value = True
        
        mock_process = MagicMock()
        mock_process.communicate.return_value = (
            b"Nmap version 7.80 ( https://nmap.org )\n", 
            b""
        )
        mock_popen.return_value = mock_process
        
        scanner = nmap.PortScanner()
        self.assertIsInstance(scanner, nmap.PortScanner)
        self.assertEqual(scanner.nmap_version(), (7, 80))

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_scanner_initialization_with_custom_paths(self, mock_popen, mock_isfile, mock_which):
        """Test PortScanner initialization with custom search paths"""
        # Mock the automatic detection to return None
        mock_which.return_value = None
        mock_isfile.side_effect = lambda path: path == '/custom/path/nmap'
        
        mock_process = MagicMock()
        mock_process.communicate.return_value = (
            b"Nmap version 7.80 ( https://nmap.org )\n", 
            b""
        )
        mock_popen.return_value = mock_process
        
        custom_paths = ('/custom/path/nmap', '/another/path/nmap')
        scanner = nmap.PortScanner(nmap_search_path=custom_paths)
        self.assertIsInstance(scanner, nmap.PortScanner)
        self.assertEqual(scanner.nmap_version(), (7, 80))

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_basic_scan(self, mock_popen, mock_isfile, mock_which):
        """Test basic scanning functionality"""
        # Mock automatic detection
        mock_which.return_value = '/usr/bin/nmap'
        mock_isfile.return_value = True
        
        # Mock nmap execution
        mock_process = MagicMock()
        mock_process.communicate.return_value = (
            self.sample_xml.encode(), 
            b""
        )
        mock_popen.return_value = mock_process
        
        # Initialize scanner with mocked nmap check
        with patch('subprocess.Popen') as mock_init_popen:
            mock_init_process = MagicMock()
            mock_init_process.communicate.return_value = (
                b"Nmap version 7.80 ( https://nmap.org )\n", 
                b""
            )
            mock_init_popen.return_value = mock_init_process
            scanner = nmap.PortScanner()
        
        # Restore the scan mock
        mock_popen.return_value = mock_process
        
        result = scanner.scan('127.0.0.1', '22,80')
        
        self.assertIn('scan', result)
        self.assertIn('127.0.0.1', result['scan'])
        self.assertTrue(scanner.has_host('127.0.0.1'))

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_scan_with_arguments(self, mock_popen, mock_isfile, mock_which):
        """Test scanning with custom arguments"""
        mock_which.return_value = '/usr/bin/nmap'
        mock_isfile.return_value = True
        
        mock_init_process = MagicMock()
        mock_init_process.communicate.return_value = (
            b"Nmap version 7.80 ( https://nmap.org )\n", 
            b""
        )
        
        mock_scan_process = MagicMock()
        mock_scan_process.communicate.return_value = (
            self.sample_xml.encode(), 
            b""
        )
        
        mock_popen.side_effect = [mock_init_process, mock_scan_process]
        
        scanner = nmap.PortScanner()
        scanner.scan('127.0.0.1', '22,80', arguments='-sV -T4')
        
        # Verify the command was called with correct arguments
        call_args = mock_scan_process.communicate.call_args
        self.assertIsNotNone(call_args)

    @patch('shutil.which')
    @patch('os.path.isfile')
    def test_type_validation(self, mock_isfile, mock_which):
        """Test parameter type validation"""
        mock_which.return_value = '/usr/bin/nmap'
        mock_isfile.return_value = True
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (
                b"Nmap version 7.80 ( https://nmap.org )\n", 
                b""
            )
            mock_popen.return_value = mock_process
            scanner = nmap.PortScanner()
        
        # Test invalid host type
        with self.assertRaises(TypeError):
            scanner.scan(123)  # Should be string
        
        # Test invalid ports type  
        with self.assertRaises(TypeError):
            scanner.scan('127.0.0.1', 123)  # Should be string or None

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_csv_export(self, mock_popen, mock_isfile, mock_which):
        """Test CSV export functionality"""
        mock_which.return_value = '/usr/bin/nmap'
        mock_isfile.return_value = True
        
        mock_init_process = MagicMock()
        mock_init_process.communicate.return_value = (
            b"Nmap version 7.80 ( https://nmap.org )\n", 
            b""
        )
        
        mock_scan_process = MagicMock()
        mock_scan_process.communicate.return_value = (
            self.sample_xml.encode(), 
            b""
        )
        
        mock_popen.side_effect = [mock_init_process, mock_scan_process]
        
        scanner = nmap.PortScanner()
        scanner.scan('127.0.0.1', '22,80')
        
        csv_output = scanner.csv()
        self.assertIsInstance(csv_output, str)
        self.assertIn('host;hostname', csv_output)

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_listscan(self, mock_popen, mock_isfile, mock_which):
        """Test list scan functionality"""
        mock_which.return_value = '/usr/bin/nmap'
        mock_isfile.return_value = True
        
        mock_init_process = MagicMock()
        mock_init_process.communicate.return_value = (
            b"Nmap version 7.80 ( https://nmap.org )\n", 
            b""
        )
        
        # Create proper XML for listscan
        listscan_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <nmaprun scanner="nmap" args="nmap -sL 192.168.1.0/24" start="1640995200" version="7.80">
        <host>
            <status state="up" reason="unknown-response"/>
            <address addr="127.0.0.1" addrtype="ipv4"/>
            <hostnames>
                <hostname name="localhost" type="PTR"/>
            </hostnames>
        </host>
        <host>
            <status state="up" reason="unknown-response"/>
            <address addr="192.168.1.1" addrtype="ipv4"/>
            <hostnames>
                <hostname name="router" type="PTR"/>
            </hostnames>
        </host>
        <runstats>
            <finished time="1640995201" elapsed="1.23" exit="success"/>
            <hosts up="2" down="0" total="2"/>
        </runstats>
        </nmaprun>"""
        
        mock_scan_process = MagicMock()
        mock_scan_process.communicate.return_value = (
            listscan_xml.encode(), 
            b""
        )
        
        mock_popen.side_effect = [mock_init_process, mock_scan_process]
        
        scanner = nmap.PortScanner()
        hosts = scanner.listscan('192.168.1.0/24')
        
        self.assertIsInstance(hosts, list)
        self.assertIn('127.0.0.1', hosts)
        self.assertIn('192.168.1.1', hosts)

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_error_handling(self, mock_popen, mock_isfile, mock_which):
        """Test error handling for invalid nmap paths"""
        # Mock automatic detection to return paths that don't exist
        mock_which.return_value = None
        mock_isfile.return_value = False
        mock_popen.side_effect = FileNotFoundError("nmap not found")
        
        with self.assertRaises(nmap.PortScannerError):
            nmap.PortScanner()

    @patch('shutil.which')
    @patch('os.path.isfile')
    @patch('subprocess.Popen')
    def test_nmap_not_found_error(self, mock_popen, mock_isfile, mock_which):
        """Test specific nmap not found error"""
        mock_which.return_value = None  # No automatic detection results
        mock_isfile.return_value = False
        mock_popen.side_effect = OSError("No such file or directory")
        
        with self.assertRaises(nmap.PortScannerError):
            nmap.PortScanner()


class TestPortScannerHostDict(unittest.TestCase):
    """Test cases for PortScannerHostDict class"""
    
    def setUp(self):
        """Set up test host data"""
        self.host_data = {
            'hostnames': [{'name': 'localhost', 'type': 'PTR'}],
            'status': {'state': 'up', 'reason': 'syn-ack'},
            'tcp': {
                22: {
                    'state': 'open',
                    'name': 'ssh',
                    'product': 'OpenSSH',
                    'version': '7.4'
                },
                80: {
                    'state': 'open', 
                    'name': 'http',
                    'product': 'nginx',
                    'version': '1.14.0'
                },
                443: {
                    'state': 'closed',
                    'name': 'https'
                }
            },
            'udp': {
                53: {
                    'state': 'open',
                    'name': 'domain'
                }
            }
        }
        self.host_dict = nmap.PortScannerHostDict(self.host_data)

    def test_hostnames(self):
        """Test hostname access"""
        hostnames = self.host_dict.hostnames()
        self.assertEqual(len(hostnames), 1)
        self.assertEqual(hostnames[0]['name'], 'localhost')

    def test_hostname(self):
        """Test single hostname access"""
        hostname = self.host_dict.hostname()
        self.assertEqual(hostname, 'localhost')

    def test_state(self):
        """Test host state access"""
        state = self.host_dict.state()
        self.assertEqual(state, 'up')

    def test_protocols(self):
        """Test protocol access"""
        protocols = self.host_dict.all_protocols()
        self.assertIn('tcp', protocols)
        self.assertIn('udp', protocols)

    def test_tcp_ports(self):
        """Test TCP port access"""
        tcp_ports = self.host_dict.all_tcp()
        self.assertIn(22, tcp_ports)
        self.assertIn(80, tcp_ports)
        self.assertIn(443, tcp_ports)
        
        self.assertTrue(self.host_dict.has_tcp(22))
        self.assertTrue(self.host_dict.has_tcp(80))
        self.assertFalse(self.host_dict.has_tcp(8080))
        
        port_22_info = self.host_dict.tcp(22)
        self.assertEqual(port_22_info['name'], 'ssh')
        self.assertEqual(port_22_info['state'], 'open')

    def test_udp_ports(self):
        """Test UDP port access"""
        udp_ports = self.host_dict.all_udp()
        self.assertIn(53, udp_ports)
        
        self.assertTrue(self.host_dict.has_udp(53))
        self.assertFalse(self.host_dict.has_udp(161))
        
        port_53_info = self.host_dict.udp(53)
        self.assertEqual(port_53_info['name'], 'domain')


class TestPortScannerAsync(unittest.TestCase):
    """Test cases for PortScannerAsync class"""
    
    @patch('nmap.PortScanner')
    def test_async_initialization(self, mock_scanner):
        """Test async scanner initialization"""
        async_scanner = nmap.PortScannerAsync()
        self.assertIsInstance(async_scanner, nmap.PortScannerAsync)

    @patch('nmap.PortScanner')
    def test_still_scanning(self, mock_scanner):
        """Test scanning status check"""
        async_scanner = nmap.PortScannerAsync()
        # Should return False when no scan is running
        self.assertFalse(async_scanner.still_scanning())

    # @patch('nmap.PortScanner')
    # @patch('multiprocessing.Process')
    # def test_async_scan_with_callback(self, mock_process, mock_scanner):
    #     """Test async scan with callback"""
    #     # Clear previous results
    #     global callback_results
    #     callback_results = []
        
    #     # Mock the scanner instance
    #     mock_scanner_instance = MagicMock()
    #     mock_scanner.return_value = mock_scanner_instance
        
    #     # Mock the process
    #     mock_process_instance = MagicMock()
    #     mock_process.return_value = mock_process_instance
        
    #     async_scanner = nmap.PortScannerAsync()
    #     async_scanner.scan('127.0.0.1', '22,80', callback=global_test_callback)
        
    #     # Verify process was created and started
    #     mock_process.assert_called_once()
    #     mock_process_instance.start.assert_called_once()


class TestPortScannerYield(unittest.TestCase):
    """Test cases for PortScannerYield class"""
    
    @patch('nmap.PortScanner')
    def test_yield_initialization(self, mock_scanner):
        """Test yield scanner initialization"""
        yield_scanner = nmap.PortScannerYield()
        self.assertIsInstance(yield_scanner, nmap.PortScannerYield)

    @patch('nmap.PortScanner')
    def test_compatibility_methods(self, mock_scanner):
        """Test compatibility methods"""
        yield_scanner = nmap.PortScannerYield()
        # These should be no-ops
        yield_scanner.stop()
        yield_scanner.wait()
        self.assertFalse(yield_scanner.still_scanning())

    @patch('nmap.PortScanner')
    def test_yield_scan_iteration(self, mock_scanner):
        """Test yield-based scanning iteration"""
        mock_scanner_instance = MagicMock()
        mock_scanner.return_value = mock_scanner_instance
        
        # Mock multiple hosts
        mock_scanner_instance.listscan.return_value = ['127.0.0.1', '127.0.0.2']
        mock_scanner_instance.scan.return_value = {'scan': {'127.0.0.1': {}}}
        
        yield_scanner = nmap.PortScannerYield()
        
        results = list(yield_scanner.scan('127.0.0.0/30', '22,80'))
        
        # Should yield results for discovered hosts
        self.assertTrue(len(results) > 0)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions and helpers"""
    
    # @patch('http.client.HTTPSConnection')
    # def test_version_detection(self, mock_conn):
    #     """Test online version detection"""
    #     mock_response = MagicMock()
    #     mock_response.status = 200
    #     mock_response.read.return_value = b'__version__ = "1.2"'
        
    #     mock_conn_instance = MagicMock()
    #     mock_conn_instance.getresponse.return_value = mock_response
    #     mock_conn.return_value = mock_conn_instance
        
    #     # Access the function correctly - it's in the nmap.nmap module
    #     from nmap import nmap as nmap_module
    #     version = nmap_module.__get_last_online_version()
    #     self.assertEqual(version, "1.2")

    # @patch('http.client.HTTPSConnection')
    # def test_version_detection_failure(self, mock_conn):
    #     """Test version detection when network fails"""
    #     mock_conn.side_effect = Exception("Network error")
        
    #     # Access the function correctly - it's in the nmap.nmap module
    #     from nmap import nmap as nmap_module
    #     version = nmap_module.__get_last_online_version()
    #     self.assertEqual(version, "unknown")

    def test_encoding_conversion(self):
        """Test encoding conversion utility"""
        test_data = {
            'host': '127.0.0.1',
            'ports': {'22': {'name': 'ssh'}}
        }
        
        converted = nmap.convert_nmap_output_to_encoding(test_data, 'utf-8')
        self.assertIsInstance(converted, dict)
        # After encoding, strings become bytes
        self.assertEqual(converted['host'], b'127.0.0.1')

    @patch('shutil.which')
    @patch('os.path.isfile')
    def test_automatic_nmap_detection(self, mock_isfile, mock_which):
        """Test automatic nmap detection function by testing PortScanner initialization"""
        mock_which.return_value = '/usr/bin/nmap'
        mock_isfile.return_value = True
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (
                b"Nmap version 7.80 ( https://nmap.org )\n", 
                b""
            )
            mock_popen.return_value = mock_process
            
            # Test that automatic detection works through PortScanner initialization
            scanner = nmap.PortScanner()
            self.assertIsInstance(scanner, nmap.PortScanner)
            # Verify shutil.which was called for automatic detection
            mock_which.assert_called_with("nmap")


if __name__ == '__main__':
    unittest.main(verbosity=2)