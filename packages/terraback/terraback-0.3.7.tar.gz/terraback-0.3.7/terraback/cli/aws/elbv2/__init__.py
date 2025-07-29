from terraback.core.license import require_professional
import typer
from pathlib import Path

from .load_balancers import scan_load_balancers, list_load_balancers, import_load_balancer
from .target_groups import scan_target_groups, list_target_groups, import_target_group
from .listeners import scan_listeners, list_listeners, import_listener
from .listener_rules import scan_listener_rules, list_listener_rules, import_listener_rule
from .ssl_policies import scan_ssl_policies, list_ssl_policies, import_ssl_policy
from .waf_associations import scan_waf_associations, list_waf_associations, import_waf_association
from .target_group_attachments import scan_target_group_attachments, list_target_group_attachments, import_target_group_attachment

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="elbv2",
    help="Manage ELB v2 (ALB/NLB/GWLB) resources including advanced listener features.",
    no_args_is_help=True
)

# --- Load Balancer Commands ---
@app.command(name="scan-lbs", help="Scan Application/Network/Gateway Load Balancers.")
@require_professional
def scan_lbs_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    lb_type: str = typer.Option(None, help="Filter by load balancer type (application/network/gateway)")
):
    scan_load_balancers(output_dir, profile, region, lb_type)

@app.command(name="list-lbs", help="List scanned Load Balancers.")
@require_professional
def list_lbs_command(output_dir: Path = typer.Option("generated")):
    list_load_balancers(output_dir)

@app.command(name="import-lb", help="Import a Load Balancer by ARN.")
@require_professional
def import_lb_command(lb_arn: str, output_dir: Path = typer.Option("generated")):
    import_load_balancer(lb_arn, output_dir)

# --- Target Group Commands ---
@app.command(name="scan-tgs", help="Scan Target Groups.")
@require_professional
def scan_tgs_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_target_groups(output_dir, profile, region)

@app.command(name="list-tgs", help="List scanned Target Groups.")
@require_professional
def list_tgs_command(output_dir: Path = typer.Option("generated")):
    list_target_groups(output_dir)

@app.command(name="import-tg", help="Import a Target Group by ARN.")
@require_professional
def import_tg_command(tg_arn: str, output_dir: Path = typer.Option("generated")):
    import_target_group(tg_arn, output_dir)

# --- Target Group Attachment Commands ---
@app.command(name="scan-targets", help="Scan Target Group Attachments (registered targets).")
@require_professional
def scan_targets_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    target_group_arn: str = typer.Option(None, help="Filter by specific target group ARN")
):
    scan_target_group_attachments(output_dir, profile, region, target_group_arn)

@app.command(name="list-targets", help="List scanned Target Group Attachments.")
@require_professional
def list_targets_command(output_dir: Path = typer.Option("generated")):
    list_target_group_attachments(output_dir)

@app.command(name="import-target", help="Import a Target Group Attachment.")
@require_professional
def import_target_command(
    target_group_arn: str = typer.Argument(..., help="Target Group ARN"),
    target_id: str = typer.Argument(..., help="Target ID (instance ID, IP, or Lambda ARN)"),
    port: str = typer.Argument(..., help="Port number"),
    output_dir: Path = typer.Option("generated")
):
    import_target_group_attachment(target_group_arn, target_id, port, output_dir)

# --- Listener Commands ---
@app.command(name="scan-listeners", help="Scan Load Balancer Listeners.")
@require_professional
def scan_listeners_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_listeners(output_dir, profile, region)

@app.command(name="list-listeners", help="List scanned Listeners.")
@require_professional
def list_listeners_command(output_dir: Path = typer.Option("generated")):
    list_listeners(output_dir)

@app.command(name="import-listener", help="Import a Listener by ARN.")
@require_professional
def import_listener_command(listener_arn: str, output_dir: Path = typer.Option("generated")):
    import_listener(listener_arn, output_dir)

# --- Listener Rule Commands ---
@app.command(name="scan-listener-rules", help="Scan ALB Listener Rules.")
@require_professional
def scan_listener_rules_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    listener_arn: str = typer.Option(None, help="Filter by specific listener ARN")
):
    scan_listener_rules(output_dir, profile, region, listener_arn)

@app.command(name="list-listener-rules", help="List scanned Listener Rules.")
@require_professional
def list_listener_rules_command(output_dir: Path = typer.Option("generated")):
    list_listener_rules(output_dir)

@app.command(name="import-listener-rule", help="Import a Listener Rule by ARN.")
@require_professional
def import_listener_rule_command(rule_arn: str, output_dir: Path = typer.Option("generated")):
    import_listener_rule(rule_arn, output_dir)

# --- SSL Policy Commands ---
@app.command(name="scan-ssl-policies", help="Scan ELB SSL Policies.")
@require_professional
def scan_ssl_policies_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_ssl_policies(output_dir, profile, region)

@app.command(name="list-ssl-policies", help="List scanned SSL Policies.")
@require_professional
def list_ssl_policies_command(output_dir: Path = typer.Option("generated")):
    list_ssl_policies(output_dir)

@app.command(name="import-ssl-policy", help="Import an SSL Policy by name.")
@require_professional
def import_ssl_policy_command(policy_name: str, output_dir: Path = typer.Option("generated")):
    import_ssl_policy(policy_name, output_dir)

# --- WAF Association Commands ---
@app.command(name="scan-waf", help="Scan WAF WebACL associations with ALBs.")
@require_professional
def scan_waf_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_waf_associations(output_dir, profile, region)

@app.command(name="list-waf", help="List scanned WAF associations.")
@require_professional
def list_waf_command(output_dir: Path = typer.Option("generated")):
    list_waf_associations(output_dir)

@app.command(name="import-waf", help="Import a WAF WebACL association.")
@require_professional
def import_waf_command(
    resource_arn: str = typer.Argument(..., help="ALB ARN"),
    web_acl_arn: str = typer.Argument(..., help="WebACL ARN"),
    output_dir: Path = typer.Option("generated")
):
    import_waf_association(resource_arn, web_acl_arn, output_dir)

# --- Enhanced "Scan All" Command ---
@app.command(name="scan-all", help="Scan all ELB v2 resources including advanced features.")
@require_professional
def scan_all_elbv2_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_ssl_policies: bool = typer.Option(True, help="Include SSL policy scanning"),
    include_attachments: bool = typer.Option(True, help="Include target group attachments"),
    include_waf: bool = typer.Option(True, help="Include WAF associations")
):
    scan_load_balancers(output_dir, profile, region)
    scan_target_groups(output_dir, profile, region)
    scan_listeners(output_dir, profile, region)
    scan_listener_rules(output_dir, profile, region)
    if include_ssl_policies:
        scan_ssl_policies(output_dir, profile, region)
    if include_attachments:
        scan_target_group_attachments(output_dir, profile, region)
    if include_waf:
        scan_waf_associations(output_dir, profile, region)

# --- Registration Function ---
def register():
    """Registers the scan functions and dependencies for the ELB v2 module."""
    
    # Load Balancers
    register_scan_function("elbv2_load_balancer", scan_load_balancers)
    cross_scan_registry.register_dependency("elbv2_load_balancer", "subnet")
    cross_scan_registry.register_dependency("elbv2_load_balancer", "security_group")
    cross_scan_registry.register_dependency("elbv2_load_balancer", "eip")  # For NLB static IPs
    
    # Target Groups
    register_scan_function("elbv2_target_group", scan_target_groups)
    cross_scan_registry.register_dependency("elbv2_target_group", "vpc")
    
    # Target Group Attachments
    register_scan_function("elbv2_target_group_attachment", scan_target_group_attachments)
    cross_scan_registry.register_dependency("elbv2_target_group_attachment", "elbv2_target_group")
    cross_scan_registry.register_dependency("elbv2_target_group_attachment", "ec2")
    cross_scan_registry.register_dependency("elbv2_target_group_attachment", "lambda_function")
    
    # Listeners
    register_scan_function("elbv2_listener", scan_listeners)
    cross_scan_registry.register_dependency("elbv2_listener", "elbv2_load_balancer")
    cross_scan_registry.register_dependency("elbv2_listener", "elbv2_target_group")
    cross_scan_registry.register_dependency("elbv2_listener", "acm_certificate")
    
    # Listener Rules
    register_scan_function("elbv2_listener_rule", scan_listener_rules)
    cross_scan_registry.register_dependency("elbv2_listener_rule", "elbv2_listener")
    cross_scan_registry.register_dependency("elbv2_listener_rule", "elbv2_target_group")
    cross_scan_registry.register_dependency("elbv2_listener_rule", "cognito_user_pool")
    
    # SSL Policies
    register_scan_function("elbv2_ssl_policy", scan_ssl_policies)
    cross_scan_registry.register_dependency("elbv2_listener", "elbv2_ssl_policy")
    
    # WAF Associations
    register_scan_function("wafv2_web_acl_association", scan_waf_associations)
    cross_scan_registry.register_dependency("wafv2_web_acl_association", "elbv2_load_balancer")
    cross_scan_registry.register_dependency("wafv2_web_acl_association", "wafv2_web_acl")