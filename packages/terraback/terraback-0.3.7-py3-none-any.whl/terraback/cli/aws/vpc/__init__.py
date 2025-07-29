import typer
from pathlib import Path
from functools import partial

from .vpcs import scan_vpcs, list_vpcs, import_vpc
from .subnets import scan_subnets, list_subnets, import_subnets
from .security_groups import scan_security_groups, list_security_groups, import_security_groups
from .internet_gateways import scan_internet_gateways, list_internet_gateways, import_internet_gateway
from .nat_gateways import scan_nat_gateways, list_nat_gateways, import_nat_gateway
from .route_tables import scan_route_tables, list_route_tables, import_route_table
from .vpc_endpoints import scan_vpc_endpoints, list_vpc_endpoints, import_vpc_endpoint

from terraback.utils.cross_scan_registry import (
    register_scan_function,
    cross_scan_registry,
    recursive_scan
)

app = typer.Typer(
    name="vpc",
    help="Manage VPC resources like VPCs, subnets, Security Groups, and networking components.",
    no_args_is_help=True
)

# --- VPC Commands ---
@app.command(name="scan", help="Scan VPCs and generate Terraform code.")
def scan_vpcs_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_vpcs(output_dir, profile, region)

@app.command(name="list", help="List scanned VPCs.")
def list_vpcs_command(output_dir: Path = typer.Option("generated")):
    list_vpcs(output_dir)

@app.command(name="import", help="Import a VPC by ID.")
def import_vpc_command(vpc_id: str, output_dir: Path = typer.Option("generated")):
    import_vpc(vpc_id, output_dir)

# --- Subnet Commands ---
@app.command(name="scan-subnets", help="Scan subnets...")
def scan_subnets_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_subnets(output_dir, profile, region)

@app.command(name="list-subnets", help="List scanned subnets.")
def list_subnets_command(output_dir: Path = typer.Option("generated")):
    list_subnets(output_dir)

@app.command(name="import-subnet", help="Import a subnet by ID.")
def import_subnet_command(subnet_id: str, output_dir: Path = typer.Option("generated")):
    import_subnets(subnet_id, output_dir)

# --- Security Group Commands ---
@app.command(name="scan-security-groups", help="Scan Security Groups...")
def scan_sg_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region..."),
    include_all: bool = typer.Option(False, help="Include default SGs.")
):
    scan_security_groups(output_dir, profile, region, include_all)

@app.command(name="list-security-groups", help="List scanned Security Groups.")
def list_sg_command(output_dir: Path = typer.Option("generated")):
    list_security_groups(output_dir)

@app.command(name="import-security-group", help="Import a Security Group by ID.")
def import_sg_command(sg_id: str, output_dir: Path = typer.Option("generated")):
    import_security_groups(sg_id, output_dir)

# --- Internet Gateway Commands ---
@app.command(name="scan-internet-gateways", help="Scan Internet Gateways.")
def scan_igw_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_internet_gateways(output_dir, profile, region)

@app.command(name="list-internet-gateways", help="List scanned Internet Gateways.")
def list_igw_command(output_dir: Path = typer.Option("generated")):
    list_internet_gateways(output_dir)

@app.command(name="import-internet-gateway", help="Import an Internet Gateway by ID.")
def import_igw_command(igw_id: str, output_dir: Path = typer.Option("generated")):
    import_internet_gateway(igw_id, output_dir)

# --- NAT Gateway Commands ---
@app.command(name="scan-nat-gateways", help="Scan NAT Gateways.")
def scan_natgw_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_nat_gateways(output_dir, profile, region)

@app.command(name="list-nat-gateways", help="List scanned NAT Gateways.")
def list_natgw_command(output_dir: Path = typer.Option("generated")):
    list_nat_gateways(output_dir)

@app.command(name="import-nat-gateway", help="Import a NAT Gateway by ID.")
def import_natgw_command(natgw_id: str, output_dir: Path = typer.Option("generated")):
    import_nat_gateway(natgw_id, output_dir)

# --- Route Table Commands ---
@app.command(name="scan-route-tables", help="Scan Route Tables.")
def scan_rt_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_route_tables(output_dir, profile, region)

@app.command(name="list-route-tables", help="List scanned Route Tables.")
def list_rt_command(output_dir: Path = typer.Option("generated")):
    list_route_tables(output_dir)

@app.command(name="import-route-table", help="Import a Route Table by ID.")
def import_rt_command(rt_id: str, output_dir: Path = typer.Option("generated")):
    import_route_table(rt_id, output_dir)

# --- VPC Endpoint Commands ---
@app.command(name="scan-endpoints", help="Scan VPC Endpoints.")
def scan_endpoint_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_vpc_endpoints(output_dir, profile, region)

@app.command(name="list-endpoints", help="List scanned VPC Endpoints.")
def list_endpoint_command(output_dir: Path = typer.Option("generated")):
    list_vpc_endpoints(output_dir)

@app.command(name="import-endpoint", help="Import a VPC Endpoint by ID.")
def import_endpoint_command(endpoint_id: str, output_dir: Path = typer.Option("generated")):
    import_vpc_endpoint(endpoint_id, output_dir)

# --- "Scan All" Command ---
@app.command(name="scan-all", help="Scan all VPC-related resources.")
def scan_all_vpc_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    with_deps: bool = typer.Option(False, help="Recursively scan dependencies from VPCs")
):
    if with_deps:
        recursive_scan("vpc", output_dir=output_dir, profile=profile, region=region)
    else:
        scan_vpcs(output_dir, profile, region)
        scan_subnets(output_dir, profile, region)
        scan_security_groups(output_dir, profile, region, include_all=True)
        scan_internet_gateways(output_dir, profile, region)
        scan_nat_gateways(output_dir, profile, region)
        scan_route_tables(output_dir, profile, region)
        scan_vpc_endpoints(output_dir, profile, region)

# --- Registration Function ---
def register():
    """Registers the scan functions and dependencies for the VPC module."""
    
    # VPC
    register_scan_function("vpc", scan_vpcs)

    # Subnets
    register_scan_function("subnets", scan_subnets)
    cross_scan_registry.register_dependency("subnets", "vpc")
    cross_scan_registry.register_dependency("subnets", "route_table")

    # Security Groups
    scan_sg_core = partial(scan_security_groups, include_all=True)
    register_scan_function("security_groups", scan_sg_core)
    cross_scan_registry.register_dependency("security_groups", "vpc")

    # Internet Gateways
    register_scan_function("internet_gateway", scan_internet_gateways)
    cross_scan_registry.register_dependency("internet_gateway", "vpc")

    # NAT Gateways
    register_scan_function("nat_gateway", scan_nat_gateways)
    cross_scan_registry.register_dependency("nat_gateway", "subnets")
    cross_scan_registry.register_dependency("nat_gateway", "eip")

    # Route Tables
    register_scan_function("route_table", scan_route_tables)
    cross_scan_registry.register_dependency("route_table", "vpc")
    cross_scan_registry.register_dependency("route_table", "internet_gateway")
    cross_scan_registry.register_dependency("route_table", "nat_gateway")

    # VPC Endpoints
    register_scan_function("vpc_endpoint", scan_vpc_endpoints)
    cross_scan_registry.register_dependency("vpc_endpoint", "vpc")
    cross_scan_registry.register_dependency("vpc_endpoint", "subnets")
    cross_scan_registry.register_dependency("vpc_endpoint", "security_groups")
    cross_scan_registry.register_dependency("vpc_endpoint", "route_table")