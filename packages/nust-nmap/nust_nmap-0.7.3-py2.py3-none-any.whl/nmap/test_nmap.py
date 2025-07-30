"""
test_nmap.py - test cases for python-nmap

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

Licence : GPL v3 or any later version
"""

import os
from multiprocessing import Value

import pytest

import nmap

nm = nmap.PortScanner()


def xmlfile_read_setup():
    if not os.path.exists("scanme_output.xml"):
        pytest.skip("scanme_output.xml not found in current directory")
    nm.analyse_nmap_xml_scan(open("scanme_output.xml").read())


def xmlfile_read_setup_multiple_osmatch():
    if not os.path.exists("osmatch_output.xml"):
        pytest.skip("osmatch_output.xml not found in current directory")
    nm.analyse_nmap_xml_scan(open("osmatch_output.xml").read())


def scan_localhost_sudo_arg_O():
    lastnm = nm.get_nmap_last_output()
    if len(lastnm) > 0:
        try:
            nm.analyse_nmap_xml_scan(lastnm)
        except Exception:
            pass
        else:
            if nm.command_line() == "nmap -oX - -O 127.0.0.1":
                return
    if hasattr(os, "getuid") and os.getuid() == 0:
        nm.scan("127.0.0.1", arguments="-O")
    else:
        nm.scan("127.0.0.1", arguments="-O", sudo=True)


def test_wrong_args():
    with pytest.raises(nmap.PortScannerError):
        nm.scan(arguments="-wrongargs")


def test_host_scan_error():
    result = nm.scan("noserver.example.com", arguments="-sP")
    assert "error" in result["nmap"]["scaninfo"]


def test_nmap_version():
    version = nm.nmap_version()
    assert isinstance(version, tuple)
    assert len(version) == 2
    assert all(isinstance(v, int) for v in version)


def test_get_nmap_last_output():
    output = nm.get_nmap_last_output()
    assert isinstance(output, str)


def test_has_host_true_false():
    nm.scan("127.0.0.1")
    assert nm.has_host("127.0.0.1") is True
    assert nm.has_host("192.0.2.1") is False


def test_scaninfo_and_scanstats_types():
    nm.scan("127.0.0.1")
    scaninfo = nm.scaninfo()
    scanstats = nm.scanstats()
    assert isinstance(scaninfo, dict)
    assert isinstance(scanstats, dict)


def test_all_hosts_sorted():
    nm.scan("127.0.0.1,127.0.0.2")
    hosts = nm.all_hosts()
    assert hosts == sorted(hosts)


def test_portscannerhostdict_methods():
    nm.scan("127.0.0.1")
    host = nm[nm.all_hosts()[0]]
    assert isinstance(host.hostnames(), list)
    assert isinstance(host.hostname(), str)
    assert isinstance(host.state(), str)
    assert isinstance(host.uptime(), dict)
    assert isinstance(host.all_protocols(), list)
    assert isinstance(host.all_tcp(), list)
    assert isinstance(host.has_tcp(22), bool)
    assert isinstance(host.all_udp(), list)
    assert isinstance(host.has_udp(53), bool)
    assert isinstance(host.all_ip(), list)
    assert isinstance(host.has_ip(1), bool)
    assert isinstance(host.all_sctp(), list)
    assert isinstance(host.has_sctp(1), bool)


def test_portscannererror_repr_str():
    err = nmap.PortScannerError("fail")
    assert "fail" in str(err)
    assert "PortScannerError" in repr(err)


def test_portscannertimeout_repr():
    err = nmap.PortScannerTimeout()
    assert "PortScannerTimeout" in repr(err)


def test_convert_nmap_output_to_encoding_bytes():
    data = {"foo": "bar", "baz": ["qux", "quux"]}
    out = nmap.convert_nmap_output_to_encoding(data, code="ascii")
    assert isinstance(out["foo"], bytes)
    assert isinstance(out["baz"][0], bytes)


def test_scan_info():
    nm.scan("127.0.0.1")
    info = nm.scaninfo()
    assert "tcp" in info
    assert "method" in info["tcp"]
    assert info["tcp"]["method"] == "connect"
    assert "services" in info["tcp"]


def test_all_hosts():
    xmlfile_read_setup()
    assert ["45.33.32.156"] == nm.all_hosts()


def test_host():
    xmlfile_read_setup()
    assert nm["45.33.32.156"].hostname() == "scanme.nmap.org"
    assert {"name": "scanme.nmap.org", "type": "user"} in nm["45.33.32.156"].hostnames()
    assert nm["45.33.32.156"].state() == "up"
    assert nm["45.33.32.156"].all_protocols() == ["tcp"]


def test_host_no_hostname():
    nm.scan("127.0.0.2")
    assert nm["127.0.0.2"].hostname() == ""


def test_ports():
    xmlfile_read_setup()
    ports = list(nm["45.33.32.156"]["tcp"].keys())
    ports.sort()
    assert ports == [22, 25, 80, 139, 445, 9929, 31337]
    assert nm["45.33.32.156"].has_tcp(22)
    assert not nm["45.33.32.156"].has_tcp(23)
    for key in ["conf", "cpe", "name", "product", "reason", "state", "version"]:
        assert key in nm["45.33.32.156"]["tcp"][22]
    assert "10" in nm["45.33.32.156"]["tcp"][22]["conf"]
    NMAP_XML_VERSION = os.environ.get("NMAP_XML_VERSION", "")
    if NMAP_XML_VERSION == "6.40":
        assert nm["45.33.32.156"]["tcp"][22]["cpe"] == ""
        assert nm["45.33.32.156"]["tcp"][22]["product"] == ""
        assert nm["45.33.32.156"]["tcp"][22]["version"] == ""
    else:
        assert "cpe:/o:linux:linux_kernel" in nm["45.33.32.156"]["tcp"][22]["cpe"]
        assert "OpenSSH" in nm["45.33.32.156"]["tcp"][22]["product"]
        assert "6.6.1p1 Ubuntu 2ubuntu2.13" in nm["45.33.32.156"]["tcp"][22]["version"]
    assert "ssh" in nm["45.33.32.156"]["tcp"][22]["name"]
    assert "syn-ack" in nm["45.33.32.156"]["tcp"][22]["reason"]
    assert "open" in nm["45.33.32.156"]["tcp"][22]["state"]
    assert nm["45.33.32.156"]["tcp"][22] == nm["45.33.32.156"].tcp(22)


def test_listscan_stats():
    xmlfile_read_setup()
    stats = nm.scanstats()
    assert stats["uphosts"] == "1"
    assert stats["downhosts"] == "0"
    assert stats["totalhosts"] == "1"
    assert "timestr" in stats
    assert "elapsed" in stats


def test_csv_output():
    xmlfile_read_setup()
    header = "host;hostname;hostname_type;protocol;port;name;state;product;extrainfo;reason;version;conf;cpe"
    assert nm.csv().split("\n")[0].strip() == header
    NMAP_XML_VERSION = os.environ.get("NMAP_XML_VERSION", "")
    result = None
    if NMAP_XML_VERSION == "6.40":
        result = "45.33.32.156;scanme.nmap.org;user;tcp;22;ssh;open;;protocol 2.0;syn-ack;;10;"
    elif NMAP_XML_VERSION in ("7.01", "7.70", "7.91"):
        result = '45.33.32.156;scanme.nmap.org;user;tcp;22;ssh;open;OpenSSH;"Ubuntu Linux; protocol 2.0";syn-ack;6.6.1p1 Ubuntu 2ubuntu2.13;10;cpe:/o:linux:linux_kernel'
    if result is not None:
        assert nm.csv().split("\n")[1].strip() == result


def test_listscan():
    assert len(nm.listscan("192.168.1.0/30")) > 0
    assert nm.listscan("localhost/30") == [
        "127.0.0.0",
        "127.0.0.1",
        "127.0.0.2",
        "127.0.0.3",
    ]


def test_ipv6():
    if hasattr(os, "getuid") and os.getuid() == 0:
        nm.scan("127.0.0.1", arguments="-6")
    else:
        nm.scan("127.0.0.1", arguments="-6", sudo=True)


def test_ipv4_async():
    global FLAG
    FLAG = Value("i", 0)
    nma = nmap.PortScannerAsync()

    def callback_result(host, scan_result):
        global FLAG
        FLAG.value = 1

    nma.scan(hosts="127.0.0.1", arguments="-p 22 -Pn", callback=callback_result)
    while nma.still_scanning():
        nma.wait(2)
    assert FLAG.value == 1


def test_ipv6_async():
    global FLAG_ipv6
    FLAG_ipv6 = Value("i", 0)
    nma_ipv6 = nmap.PortScannerAsync()

    def callback_result(host, scan_result):
        global FLAG_ipv6
        FLAG_ipv6.value = 1

    nma_ipv6.scan(hosts="::1", arguments="-6 -p 22 -Pn", callback=callback_result)
    while nma_ipv6.still_scanning():
        nma_ipv6.wait(2)
    assert FLAG_ipv6.value == 1


def test_sudo():
    scan_localhost_sudo_arg_O()
    assert "osmatch" in nm["127.0.0.1"]
    assert len(nm["127.0.0.1"]["osmatch"][0]["osclass"]) > 0
    assert nm["127.0.0.1"]["osmatch"][0]["osclass"][0]["vendor"] == "Linux"


def test_parsing_osmap_osclass_and_others():
    scan_localhost_sudo_arg_O()
    assert "osmatch" in nm["127.0.0.1"]
    assert nm["127.0.0.1"]["osmatch"][0]["name"] == "Linux 2.6.32"
    assert "accuracy" in nm["127.0.0.1"]["osmatch"][0]
    assert "line" in nm["127.0.0.1"]["osmatch"][0]
    assert "osclass" in nm["127.0.0.1"]["osmatch"][0]
    assert nm["127.0.0.1"]["osmatch"][0]["osclass"][0]["vendor"] == "Linux"
    for key in ["type", "osfamily", "osgen", "accuracy"]:
        assert key in nm["127.0.0.1"]["osmatch"][0]["osclass"][0]


def test_all_protocols():
    scan_localhost_sudo_arg_O()
    protocols = nm["127.0.0.1"].all_protocols()
    for key in [
        "addresses",
        "hostnames",
        "status",
        "vendor",
        "osclass",
        "osmatch",
        "uptime",
        "portused",
    ]:
        assert key not in protocols
    assert "tcp" in protocols


def test_multipe_osmatch():
    xmlfile_read_setup_multiple_osmatch()
    assert "osmatch" in nm["127.0.0.1"]
    assert "portused" in nm["127.0.0.1"]
    for osm in nm["127.0.0.1"]["osmatch"]:
        for key in ["accuracy", "line", "name", "osclass"]:
            assert key in osm
        for key in ["accuracy", "cpe", "osfamily", "osgen", "type", "vendor"]:
            assert key in osm["osclass"][0]


def test_convert_nmap_output_to_encoding():
    xmlfile_read_setup()
    a = nm.analyse_nmap_xml_scan(open("scanme_output.xml").read())
    out = nmap.convert_nmap_output_to_encoding(a, code="ascii")
    assert out["scan"]["45.33.32.156"]["addresses"]["ipv4"] == b"45.33.32.156"


def test_WARNING_case_sensitive():
    nm.scan("localhost", arguments="-S 127.0.0.1")
    assert "warning" in nm.scaninfo()
    assert "WARNING" in nm.scaninfo()["warning"][0]


def test_scan_progressive():
    nmp = nmap.PortScannerAsync()

    def callback(host, scan_data):
        assert host is not None

    nmp.scan(hosts="127.0.0.1", arguments="-sV", callback=callback)
    nmp.wait()


def test_sudo_encoding__T24():
    """
    When using "sudo=True" like this 'nm.scan(hosts=ip_range, arguments="-sP", sudo = True)'
    i got a UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 9: ordinal not in range(128).
    But if sudo is false all thing work nice.
    """
    nm.scan("192.168.1.1/24", arguments="-sP", sudo=True)
