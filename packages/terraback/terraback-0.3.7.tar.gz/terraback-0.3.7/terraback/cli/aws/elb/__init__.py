from terraback.core.license import require_professional
import typer
from pathlib import Path
from .classic_load_balancers import scan_classic_lbs, list_classic_lbs, import_classic_lb
from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="elb",
    help="Manage Classic Load Balancers (ELBv1).",
    no_args_is_help=True
)

@app.command(name="scan-classic", help="Scan Classic Load Balancers.")
@require_professional
def scan_clbs_command(output_dir: Path = typer.Option("generated"), profile: str = typer.Option(None), region: str = typer.Option("us-east-1")):
    scan_classic_lbs(output_dir, profile, region)

@app.command(name="list-classic", help="List scanned Classic LBs.")
@require_professional
def list_clbs_command(output_dir: Path = typer.Option("generated")):
    list_classic_lbs(output_dir)

@app.command(name="import-classic", help="Import a Classic LB by name.")
@require_professional
def import_clb_command(lb_name: str, output_dir: Path = typer.Option("generated")):
    import_classic_lb(lb_name, output_dir)

def register():
    """Registers scan functions and dependencies for the Classic LB module."""
    register_scan_function("classic_load_balancer", scan_classic_lbs)

    # Define dependencies for Classic LBs
    cross_scan_registry.register_dependency("classic_load_balancer", "subnet")
    cross_scan_registry.register_dependency("classic_load_balancer", "security_group")
    cross_scan_registry.register_dependency("classic_load_balancer", "ec2")
    cross_scan_registry.register_dependency("classic_load_balancer", "route53_record")