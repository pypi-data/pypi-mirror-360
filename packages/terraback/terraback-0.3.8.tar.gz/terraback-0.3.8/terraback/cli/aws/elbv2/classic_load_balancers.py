from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_classic_lbs(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Classic Load Balancers (CLBs) and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    # Note: Using the older 'elb' client, not 'elbv2'
    elb_client = boto_session.client("elb")
    
    print(f"Scanning for Classic Load Balancers in region {region}...")
    paginator = elb_client.get_paginator('describe_load_balancers')
    classic_lbs = []
    for page in paginator.paginate():
        for clb in page['LoadBalancerDescriptions']:
            # Fetch tags separately for CLBs
            tags_response = elb_client.describe_tags(LoadBalancerNames=[clb['LoadBalancerName']])
            if tags_response['TagDescriptions']:
                clb['Tags'] = tags_response['TagDescriptions'][0]['Tags']
            else:
                clb['Tags'] = []
            classic_lbs.append(clb)

    output_file = output_dir / "classic_load_balancer.tf"
    generate_tf(classic_lbs, "classic_load_balancer", output_file)
    print(f"Generated Terraform for {len(classic_lbs)} Classic Load Balancers -> {output_file}")
    generate_imports_file("classic_load_balancer", classic_lbs, remote_resource_id_key="LoadBalancerName", output_dir=output_dir)

def list_classic_lbs(output_dir: Path):
    ImportManager(output_dir, "classic_load_balancer").list_all()

def import_classic_lb(lb_name: str, output_dir: Path):
    ImportManager(output_dir, "classic_load_balancer").find_and_import(lb_name)