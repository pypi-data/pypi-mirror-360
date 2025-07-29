from terraback.core.license import require_professional
import typer
from pathlib import Path

from .auto_scaling_groups import scan_auto_scaling_groups, list_auto_scaling_groups, import_auto_scaling_group
from .launch_configurations import scan_launch_configurations, list_launch_configurations, import_launch_configuration
from .scaling_policies import scan_scaling_policies, list_scaling_policies, import_scaling_policy

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="autoscaling",
    help="Manage Auto Scaling resources like Auto Scaling Groups, Launch Configurations, and Scaling Policies.",
    no_args_is_help=True
)

# --- Auto Scaling Group Commands ---
@app.command(name="scan-groups", help="Scan Auto Scaling Groups.")
@require_professional
def scan_asgs_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_auto_scaling_groups(output_dir, profile, region)

@app.command(name="list-groups", help="List scanned Auto Scaling Groups.")
@require_professional
def list_asgs_command(output_dir: Path = typer.Option("generated")):
    list_auto_scaling_groups(output_dir)

@app.command(name="import-group", help="Import an Auto Scaling Group by name.")
@require_professional
def import_asg_command(
    asg_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_auto_scaling_group(asg_name, output_dir)

# --- Launch Configuration Commands ---
@app.command(name="scan-launch-configs", help="Scan Launch Configurations.")
@require_professional
def scan_lcs_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_launch_configurations(output_dir, profile, region)

@app.command(name="list-launch-configs", help="List scanned Launch Configurations.")
@require_professional
def list_lcs_command(output_dir: Path = typer.Option("generated")):
    list_launch_configurations(output_dir)

@app.command(name="import-launch-config", help="Import a Launch Configuration by name.")
@require_professional
def import_lc_command(
    lc_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_launch_configuration(lc_name, output_dir)

# --- Scaling Policy Commands ---
@app.command(name="scan-policies", help="Scan Auto Scaling Policies.")
@require_professional
def scan_policies_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_scaling_policies(output_dir, profile, region)

@app.command(name="list-policies", help="List scanned Auto Scaling Policies.")
@require_professional
def list_policies_command(output_dir: Path = typer.Option("generated")):
    list_scaling_policies(output_dir)

@app.command(name="import-policy", help="Import an Auto Scaling Policy by name.")
@require_professional
def import_policy_command(
    policy_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_scaling_policy(policy_name, output_dir)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the Auto Scaling module."""
    register_scan_function("autoscaling_group", scan_auto_scaling_groups)
    register_scan_function("launch_configuration", scan_launch_configurations)
    register_scan_function("autoscaling_policy", scan_scaling_policies)

    # Define dependencies
    # ASG depends on Launch Templates or Launch Configurations
    cross_scan_registry.register_dependency("autoscaling_group", "launch_template")
    cross_scan_registry.register_dependency("autoscaling_group", "launch_configuration")
    # ASG depends on subnets and target groups
    cross_scan_registry.register_dependency("autoscaling_group", "subnets")
    cross_scan_registry.register_dependency("autoscaling_group", "elbv2_target_group")
    # ASG depends on scaling policies
    cross_scan_registry.register_dependency("autoscaling_group", "autoscaling_policy")
    # Launch Configurations depend on security groups, key pairs, and AMIs
    cross_scan_registry.register_dependency("launch_configuration", "security_groups")
    cross_scan_registry.register_dependency("launch_configuration", "key_pairs")
    cross_scan_registry.register_dependency("launch_configuration", "amis")
    # Scaling policies depend on CloudWatch alarms
    cross_scan_registry.register_dependency("autoscaling_policy", "cloudwatch_alarm")