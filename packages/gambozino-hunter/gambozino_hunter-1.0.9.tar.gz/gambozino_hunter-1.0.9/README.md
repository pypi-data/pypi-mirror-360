# Gambozino Hunter 🕵️‍♂️

**Gambozino Hunter** is a Python CLI tool for performing **network scans** and **vulnerability scans** with easy-to-read terminal output and JSON report generation.

It is designed for cybersecurity professionals, sysadmins, and developers who need quick insight into network assets and their potential weaknesses.

---

## 🚀 Features

- 🔍 **Network Scanner**:
  - Discovers active hosts on a subnet
  - Scans for open ports and running services
- 🛡️ **Vulnerability Scanner**:
  - Matches known patterns and vulnerabilities
- 📄 **Output**:
  - Beautiful **Rich** tables for CLI viewing
  - **JSON** reports saved locally for further analysis
- 🐍 Fully compatible with Python 3.12+

---

## 📦 Installation

You can install from [PyPI](https://pypi.org/project/gambozino-hunter/):

```bash
pip install gambozino-hunter
```

Or install locally from source:

```bash
git clone https://github.com/ScriptK-dd13s/GambozinoHunter.git
cd GambozinoHunter
pip install .
```

## 🛠️ Usage of Network Scanner

# Run from the CLI

```bash

# If you need help just type
gh --help

# Scann all of the network 192.168.1.0/24 on port 22
gh network-scanner 192.168.1.0/24 -p 22

# Use the result of the last network scann to check for vulnerabilities and store it to a specific file
gh vuln-scanner -o /home/b3rrypi/some/folder/output.json
```

## 📚 Project Structure

```
.
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
└── src
    ├── gh
    │   ├── cli.py
    │   ├── commands
    │   │   ├── __init__.py
    │   │   ├── network_scanner.py
    │   │   ├── __pycache__
    │   │   │   ├── __init__.cpython-312.pyc
    │   │   │   ├── network_scanner.cpython-312.pyc
    │   │   │   ├── portscanner.cpython-312.pyc
    │   │   │   ├── report_generation.cpython-312.pyc
    │   │   │   └── vuln_scanner.cpython-312.pyc
    │   │   └── vuln_scanner.py
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── patterns.json
    │   ├── __pycache__
    │   │   └── __init__.cpython-312.pyc
    │   └── tests
    │       └── typer_poc
    │           ├── goodbye.py
    │           ├── __init__.py
    │           └── main.py
    └── reports
        ├── gh_network_scan_report.json
        └── gh_vuln_scan_report.json
```

## 📝 License

This project is licensed under the MIT License.

## 🧠 Author & Contributing

Developed with ❤️ by [FilipeS0usa](https://github.com/FilipeS0usa) and [Grilinux](https://github.com/Grilinux). Contributions are welcome!

## TODO / Roadmap

- [ ] Add unit tests for core modules
