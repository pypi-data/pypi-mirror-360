"""
    Install : python setup.py install
    Register : python setup.py register

    platform = 'Unix',
    download_url = 'https://github.com/codeNinja62/nust-nmap',
"""
#!/usr/bin/env python

import codecs
import os

from setuptools import Command, setup

# Remove Extension import since we're not building C extensions


here = os.path.dirname(os.path.abspath(__file__))
version = "0.7.3"

"""
Version command for setuptools to display the library version.
"""


class VersionCommand(Command):
    """Custom command to print the library version."""

    description = "Show library version"
    user_options = []

    def initialize_options(self):
        """Set default values for options (none needed)."""
        pass

    def finalize_options(self):
        """Post-process options (none needed)."""
        pass

    def run(self):
        """Run the command to print the version."""
        print(version)


# Get the short description
description = "Enhanced Python 3.8+ interface to nmap with comprehensive type hints and modern error handling"

# Get the long description
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f"\n{f.read()}"

# Get change log
with codecs.open(os.path.join(here, "CHANGELOG"), encoding="utf-8") as f:
    changelog = f.read()
    long_description += f"\n\n{changelog}"

setup(
    maintainer="Sameer Ahmed",
    maintainer_email="sameer.cs@proton.me",
    # bugtrack_url='https://github.com/codeNinja62/nust-nmap',
    cmdclass={"version": VersionCommand},
    description=description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Firewalls",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    keywords="nmap, portscanner, network, sysadmin, security, vulnerability, scanning, type-hints",
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    license="gpl-3.0.txt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="nust-nmap",
    packages=["nmap"],
    platforms=[
        "Operating System :: OS Independent",
    ],
    url="https://github.com/codeNinja62/nust-nmap",
    version=version,
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies required - uses stdlib only
    ],
    extras_require={
        "dev": [
            "mypy>=1.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
        "performance": [
            "lxml>=4.6.0",  # Faster XML parsing if available
        ],
    },
    project_urls={
        "Documentation": "https://github.com/codeNinja62/nust-nmap",
        "Source": "https://github.com/codeNinja62/nust-nmap",
        "Bug Reports": "https://github.com/codeNinja62/nust-nmap/issues",
        "Changelog": "https://github.com/codeNinja62/nust-nmap/blob/main/CHANGELOG",
    },
)