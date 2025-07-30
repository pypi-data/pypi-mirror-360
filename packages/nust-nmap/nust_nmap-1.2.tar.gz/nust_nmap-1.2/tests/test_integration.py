"""
Integration tests for nust-nmap - requires actual nmap installation
"""

import unittest
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nmap


class TestIntegration(unittest.TestCase):
    """Integration tests that require actual nmap"""
    
    @classmethod
    def setUpClass(cls):
        """Check if nmap is available for integration tests"""
        try:
            cls.scanner = nmap.PortScanner()
            cls.nmap_available = True
        except nmap.PortScannerError:
            cls.nmap_available = False

    def setUp(self):
        """Skip tests if nmap is not available"""
        if not self.nmap_available:
            self.skipTest("nmap not available for integration tests")

    def test_localhost_scan(self):
        """Test scanning localhost"""
        result = self.scanner.scan('127.0.0.1', arguments='-sT -p 22,80')
        
        self.assertIn('scan', result)
        self.assertIn('nmap', result)
        self.assertIn('127.0.0.1', result['scan'])

    def test_nmap_version(self):
        """Test nmap version detection"""
        version = self.scanner.nmap_version()
        self.assertIsInstance(version, tuple)
        self.assertEqual(len(version), 2)
        self.assertGreater(version[0], 0)

    def test_csv_export_real_data(self):
        """Test CSV export with real scan data"""
        self.scanner.scan('127.0.0.1', arguments='-sT -p 22')
        csv_output = self.scanner.csv()
        
        self.assertIsInstance(csv_output, str)
        self.assertIn('127.0.0.1', csv_output)


if __name__ == '__main__':
    unittest.main(verbosity=2)