import json
import os
import re
import socket
import subprocess

import typer
from IPy import IP as IPyIP
from rich.console import Console
from rich.progress import track
from rich.table import Table
from scapy.all import *  # The One and Only Scapy
from typing_extensions import Annotated

console = Console()


def validate_ports_input(ports: str) -> list:
    single_pattern = r"^\d+$"
    dash_pattern = r"^\d+\-\d+$"
    comma_pattern = r"^\d+(\,\d+)*$"
    if re.fullmatch(single_pattern, ports):
        return [int(ports)]
    if re.fullmatch(dash_pattern, ports):
        start, end = map(int, ports.split("-"))
        return list(range(start, end + 1))
    elif re.fullmatch(comma_pattern, ports):
        return [int(p) for p in ports.split(",")]
    else:
        raise Exception(f"'{ports}' is not a valid pattern for ports option")


def check_ip(target: str) -> str:
    try:
        return IPyIP(target)
    except ValueError:
        return socket.gethostbyname(target)


def ping_target(ip: str) -> bool:
    param = "-n" if os.name == "nt" else "-c"
    try:
        subprocess.run(
            ["ping", param, "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def scan_ports(ip: str, ports: list) -> list:
    results = []

    for port in track(ports, description=f"Scanning ports for {ip}..."):
        # Stealth SYN scan
        pkt = IP(dst=ip) / TCP(dport=int(port), flags="S")
        response = sr1(pkt, timeout=0.5, verbose=0)

        port_info = {
            "port_number": port,
            "active": False,
            "service": "N/A",
        }

        if response and response.haslayer(TCP):
            if response[TCP].flags == 0x12:  # SYN-ACK
                port_info["active"] = True

                # Send RST to avoid completing handshake
                rst_pkt = IP(dst=ip) / TCP(dport=int(port), flags="R")
                sr1(rst_pkt, timeout=0.5, verbose=0)

                # Do full TCP connect to grab banner
                banner = grab_banner(ip, port)
                port_info["service"] = banner

        if port_info["active"]:
            results.append(port_info)

    return results


def grab_banner(ip: str, port: int) -> str:
    try:
        with socket.create_connection((ip, port), timeout=0.5) as sock:
            sock.settimeout(0.5)
            try:
                banner = sock.recv(1024).decode(errors="ignore").strip()
                return banner if banner else "No banner"
            except socket.timeout:
                return "No banner (timeout)"
    except Exception as e:
        return f"Connection failed: {e}"


# Main Network Scan Command
def network_scanner(
    target: Annotated[
        str,
        typer.Argument(
            help="Chose a target (IP, IP range or Network).",
        ),
    ],
    ports: Annotated[
        str,
        typer.Option(
            "--ports",
            "-p",
            help="You can chose a specific port (ex.: 22 will scan port 22), an interval of ports separated by '-' (ex.: 0-23) and specific ports separated by ',' (ex.: 22,443).",
        ),
    ] = "",
    wk_ports: Annotated[
        bool,
        typer.Option(
            "--wk-ports",
            "-wkp",
            help="Scan all well known ports (0-1023).",
        ),
    ] = False,
    registered_ports: Annotated[
        bool,
        typer.Option(
            "--registered-ports",
            "-rp",
            help="Scan all registered ports (1024-49151).",
        ),
    ] = False,
    all_ports: Annotated[
        bool,
        typer.Option(
            "--all-ports",
            "-ap",
            help="Scan all 65535 ports available.",
        ),
    ] = False,
    ping_bypass: Annotated[
        bool,
        typer.Option(
            "--ping-bypass",
            "-pB",
            help="Bypass the ping analysis.",
        ),
    ] = False,
    report_path: Annotated[
        str,
        typer.Option(
            "--report-path",
            "-R",
            help="Receive a human readable report from network-scanner. To use this option you need to supply a valid path. (Ex.: -R /some/folder)",
        ),
    ] = "",
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Choose a different output path for json file.",
        ),
    ] = "",
):
    ips = check_ip(target)

    table = Table("Target", "Ports Open", "Service")
    console.print(f"\n[bold red]Targeting[/bold red]: [cyan]{target}[/cyan] :boom:\n")

    if wk_ports:
        port_list = list(range(0, 1023 + 1))
    elif registered_ports:
        port_list = list(range(1024, 49151 + 1))
    elif all_ports:
        port_list = list(range(0, 65535 + 1))
    elif ports:
        port_list = validate_ports_input(ports)
    else:
        raise Exception(
            "You have to choose a port option (--ports, --wk-ports, --registered-ports, --all-ports), check --help for options description."
        )

    report = []

    for ip in ips:  # track(ips, description="Scanning target..."):
        ip_str = ip.strNormal()
        ip_info = {"target": ip_str, "ports": ""}

        if not ping_bypass:
            if not ping_target(ip_str):
                # console.print(f"{ip} is down!")
                continue
            # console.print(f"{ip} is up!")

        ports_info = scan_ports(ip_str, port_list)

        if ports_info:
            for port_info in ports_info:
                table.add_row(
                    ip_str, str(port_info["port_number"]), port_info["service"]
                )
            ip_info["ports"] = ports_info
            report.append(ip_info)

    console.print("\n[bold purple]Report table:[/bold purple]")

    console.print(table)

    path_cwd = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )

    path_dir = path_cwd + "/reports"
    file_name = "/gh_network_scan_report.json"

    path_final = path_dir + file_name

    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    # console.print(f"Current path: {path_final}")

    with open(path_final, "w") as fp:
        json.dump(report, fp, indent=2)

    if output:
        with open(output, "w") as fp:
            json.dump(report, fp, indent=2)

    # if report:
    #     if not os.path.exists(report):
    #         os.makedirs(report)
    # TODO: Call function that creates report from json
    # def gen_report(report, report_path)


"""
json example:

[
    {
        "target": "192.168.1.254",
        "ports": [
            { 
                "port_number": "22",
                "active": True, 
                "service": "sshd ubuntu ..."
                "vulnerability": [
                    {
                        "cve": "", 
                        "cvss": ""
                    }
                    {
                        "cve": "", 
                        "cvss": ""
                    }
                    {
                        "cve": "", 
                        "cvss": ""
                    }
                ]
            },
            {
                "port_number": "<port_number>": 
                "active": bool, 
                "service":  "<information_from_that_port>"
            }
        ],
    },
    {
        "target": "<some_ip>",
        "ports": [
            { 
                "port_number": "<some_port>",
                "active": bool, 
                "service": "<response_from_socket"
            }
        ],
    },
]
"""
