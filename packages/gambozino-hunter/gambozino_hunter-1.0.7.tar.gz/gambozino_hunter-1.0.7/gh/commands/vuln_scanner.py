import json
import os
import re

import nvdlib
import typer
from rich.console import Console
from rich.progress import track
from rich.table import Table
from typing_extensions import Annotated

console = Console()


def load_patterns(path):
    with open(path, "r") as f:
        data = json.load(f)

        return {k: tuple(v) for k, v in data.items()}


def identify_software_version(banner):
    """
    Identify software (vendor, product) and version from a banner string.
    Extend the patterns dict with regexes for more services.
    Returns (vendor, product, version) or (None, None, None) if not found.
    """

    path_src = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path_patterns = path_src + "/patterns.json"
    patterns = load_patterns(path_patterns)

    for regex, (vendor, product) in patterns.items():
        m = re.search(regex, banner, re.IGNORECASE)
        if m:
            version = m.group(1)
            return (vendor.lower(), product.lower(), version)
    return (None, None, None)


def build_cpe(vendor, product, version):
    """
    Construct a CPE string from vendor, product, and version.
    Uses 'a' (application) as the part; use 'o' for OS if appropriate.
    """
    part = "a"  # assume application by default
    # Replace spaces with underscores, ensure lowercase
    vendor = vendor.replace(" ", "_")
    product = product.replace(" ", "_")
    cpe = f"cpe:2.3:{part}:{vendor}:{product}:{version}"
    return cpe


def get_cves_for_cpe(cpe):
    """
    Query NVD for CVEs matching the given CPE string.
    Returns a list of (CVE-ID, description).
    """
    cves = []
    try:
        results = nvdlib.searchCVE(virtualMatchString=cpe)
        for cve in results:
            cve_info = {"cve_id": "", "score": ""}
            cve_info["cve_id"] = cve.id
            cve_info["score"] = cve.score
            cves.append(cve_info)
    except Exception as e:
        console.print(f"Error querying NVD for {cpe}: {e}")
    return cves


def check_vulns(service: str) -> list:
    # This function will check if there is existent CVEs for the service and return a list
    vendor, product, version = identify_software_version(service)
    if not vendor or not version:
        console.print("Could not identify software name/version from banner.")
    else:
        # console.print(
        #     f"Identified: vendor='{vendor}', product='{product}', version='{version}'"
        # )
        cpe = build_cpe(vendor, product, version)
        # console.print(f"Using CPE: {cpe}")
        cve_list = get_cves_for_cpe(cpe)
        if not cve_list:
            print("No CVEs found (or error occurred).")

    return cve_list


def vuln_scanner(
    input: Annotated[
        str,
        typer.Option(
            "--input",
            "-in",
            help="Input file, if not chosen will use last network scan that was made.",
        ),
    ] = "",
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-out",
            help="Output path for json file, if not chosen will output to default directory.",
        ),
    ] = "",
    report: Annotated[
        str,
        typer.Option(
            "--report",
            "-re",
            help="Output path for human readable report of vuln scanner, if not chosen will not output a report anywhere.",
        ),
    ] = "",
):
    table = Table("Target", "Port", "Service", "CVE", "Score")

    path_cwd = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )
    path_report = path_cwd + "/reports"

    if input:
        path_net_scan_report = input
    else:
        network_file_name = "/gh_network_scan_report.json"
        path_net_scan_report = path_report + network_file_name

    with open(path_net_scan_report, "r") as nsr:
        report = json.load(nsr)

    for target in track(report, description="Analyzing vulnerabilities..."):
        for port in target["ports"]:
            if port["service"] == "N/A" or port["service"] == "No banner (timeout)":
                continue
            vulns = check_vulns(port["service"])
            for vuln in vulns:
                table.add_row(
                    target["target"],
                    str(port["port_number"]),
                    port["service"],
                    vuln["cve_id"],
                    str(vuln["score"]),
                )

            port["vulnerabilities"] = vulns

    console.print("\n[bold purple]Report table:[/bold purple]")
    console.print(table)

    vulnscan_file_name = "/gh_vuln_scan_report.json"
    path_vuln_scan_report = path_report + vulnscan_file_name

    if not os.path.exists(path_report):
        os.makedirs(path_report)

    with open(path_vuln_scan_report, "w") as fp:
        json.dump(report, fp, indent=2)

    if output:
        with open(output, "w") as fp:
            json.dump(report, fp, indent=2)
