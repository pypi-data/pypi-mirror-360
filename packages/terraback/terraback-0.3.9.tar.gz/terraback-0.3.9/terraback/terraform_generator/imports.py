import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .filters import to_terraform_resource_name, strip_id_prefix


def detect_provider_from_resource_type(resource_type: str) -> str:
    """Detect cloud provider from resource type."""
    if any(prefix in resource_type.lower() for prefix in ['aws_', 'amazon', 'ec2', 's3', 'iam', 'lambda', 'api_gateway', 'route53', 'cloudfront', 'elb']):
        return "aws"
    elif any(prefix in resource_type.lower() for prefix in ['azure_', 'azurerm_', 'microsoft']):
        return "azure"
    elif any(prefix in resource_type.lower() for prefix in ['gcp_', 'google_', 'compute']):
        return "gcp"
    else:
        # Try to detect from resource data structure
        return "aws"  # Default to AWS


def normalize_terraform_resource_type(resource_type: str, provider: Optional[str] = None) -> str:
    """
    Convert short resource type names to full Terraform resource type names.
    
    Args:
        resource_type: Short name like 'api_gateway_deployment' or full name like 'aws_api_gateway_deployment'
        provider: Optional provider override ('aws', 'azure', 'gcp')
    
    Returns:
        Full Terraform resource type like 'aws_api_gateway_deployment'
    """
    # If already has provider prefix, return as-is
    if any(resource_type.startswith(prefix) for prefix in ['aws_', 'azurerm_', 'google_']):
        return resource_type
    
    # Detect provider if not provided
    if not provider:
        provider = detect_provider_from_resource_type(resource_type)
    
    # AWS resource type mappings
    aws_mappings = {
        # API Gateway
        'api_gateway_deployment': 'aws_api_gateway_deployment',
        'api_gateway_method': 'aws_api_gateway_method',
        'api_gateway_resource': 'aws_api_gateway_resource',
        'api_gateway_rest_api': 'aws_api_gateway_rest_api',
        'api_gateway_stage': 'aws_api_gateway_stage',
        'api_gateway_integration': 'aws_api_gateway_integration',
        
        # Compute
        'ec2': 'aws_instance',
        'ec2_instance': 'aws_instance',
        'instance': 'aws_instance',
        'instances': 'aws_instance',
        'launch_configuration': 'aws_launch_configuration',
        'autoscaling_group': 'aws_autoscaling_group',
        'autoscaling_policy': 'aws_autoscaling_policy',
        'lambda_function': 'aws_lambda_function',
        'lambda_layer_version': 'aws_lambda_layer_version',
        'lambda_permission': 'aws_lambda_permission',
        
        # Storage
        's3_bucket': 'aws_s3_bucket',
        'bucket': 'aws_s3_bucket',
        'buckets': 'aws_s3_bucket',
        'ebs_volume': 'aws_ebs_volume',
        'volume': 'aws_ebs_volume',
        'volumes': 'aws_ebs_volume',
        'ebs_snapshot': 'aws_ebs_snapshot',
        'efs_file_system': 'aws_efs_file_system',
        'efs_mount_target': 'aws_efs_mount_target',
        'efs_access_point': 'aws_efs_access_point',
        
        # Networking
        'vpc': 'aws_vpc',
        'vpcs': 'aws_vpc',
        'subnet': 'aws_subnet',
        'subnets': 'aws_subnet',
        'security_group': 'aws_security_group',
        'security_groups': 'aws_security_group',
        'internet_gateway': 'aws_internet_gateway',
        'nat_gateway': 'aws_nat_gateway',
        'route_table': 'aws_route_table',
        'network_interface': 'aws_network_interface',
        'network_interfaces': 'aws_network_interface',
        'eip': 'aws_eip',
        'eips': 'aws_eip',
        'vpc_endpoint': 'aws_vpc_endpoint',
        
        # Load Balancing
        'classic_load_balancer': 'aws_elb',
        'elbv2_load_balancer': 'aws_lb',
        'elbv2_target_group': 'aws_lb_target_group',
        'elbv2_listener': 'aws_lb_listener',
        'elbv2_listener_rule': 'aws_lb_listener_rule',
        'elbv2_target_group_attachments': 'aws_lb_target_group_attachment',
        
        # Database
        'rds_instance': 'aws_db_instance',
        'rds_parameter_group': 'aws_db_parameter_group',
        'rds_subnet_group': 'aws_db_subnet_group',
        
        # Caching
        'elasticache_redis_cluster': 'aws_elasticache_cluster',
        'elasticache_memcached_cluster': 'aws_elasticache_cluster',
        'elasticache_replication_group': 'aws_elasticache_replication_group',
        'elasticache_parameter_group': 'aws_elasticache_parameter_group',
        'elasticache_subnet_group': 'aws_elasticache_subnet_group',
        
        # Security & Identity
        'iam_role': 'aws_iam_role',
        'iam_roles': 'aws_iam_role',
        'iam_policy': 'aws_iam_policy',
        'iam_policies': 'aws_iam_policy',
        'key_pair': 'aws_key_pair',
        'key_pairs': 'aws_key_pair',
        'acm_certificate': 'aws_acm_certificate',
        'secretsmanager_secret': 'aws_secretsmanager_secret',
        'secretsmanager_secret_version': 'aws_secretsmanager_secret_version',
        
        # DNS
        'route53_zone': 'aws_route53_zone',
        'route53_record': 'aws_route53_record',
        
        # CDN
        'cloudfront_distribution': 'aws_cloudfront_distribution',
        'cloudfront_cache_policy': 'aws_cloudfront_cache_policy',
        'cloudfront_origin_request_policy': 'aws_cloudfront_origin_request_policy',
        'cloudfront_origin_access_control': 'aws_cloudfront_origin_access_control',
        
        # Monitoring
        'cloudwatch_alarm': 'aws_cloudwatch_metric_alarm',
        'cloudwatch_dashboard': 'aws_cloudwatch_dashboard',
        'cloudwatch_log_group': 'aws_cloudwatch_log_group',
        
        # Messaging
        'sns_topic': 'aws_sns_topic',
        'sns_subscription': 'aws_sns_topic_subscription',
        'sqs_queue': 'aws_sqs_queue',
        
        # Management
        'ssm_parameter': 'aws_ssm_parameter',
        'ssm_document': 'aws_ssm_document',
        'ssm_maintenance_window': 'aws_ssm_maintenance_window',
        
        # Container
        'ecr_repository': 'aws_ecr_repository',
        'ecs_cluster': 'aws_ecs_cluster',
        'ecs_service': 'aws_ecs_service',
        'ecs_task_definition': 'aws_ecs_task_definition',
    }
    
    # Azure resource type mappings
    azure_mappings = {
        'azure_virtual_machine': 'azurerm_linux_virtual_machine',  # Will be handled in template
        'azure_managed_disk': 'azurerm_managed_disk',
        'azure_virtual_network': 'azurerm_virtual_network',
        'azure_subnet': 'azurerm_subnet',
        'azure_network_security_group': 'azurerm_network_security_group',
        'azure_network_interface': 'azurerm_network_interface',
        'azure_storage_account': 'azurerm_storage_account',
        'azure_resource_group': 'azurerm_resource_group',
        'azure_lb': 'azurerm_lb',
        
        # Short names
        'vm': 'azurerm_linux_virtual_machine',
        'vms': 'azurerm_linux_virtual_machine',
        'disk': 'azurerm_managed_disk',
        'disks': 'azurerm_managed_disk',
        'vnet': 'azurerm_virtual_network',
        'vnets': 'azurerm_virtual_network',
        'nsg': 'azurerm_network_security_group',
        'nsgs': 'azurerm_network_security_group',
    }
    
    # GCP resource type mappings
    gcp_mappings = {
        'gcp_instance': 'google_compute_instance',
        'gcp_disk': 'google_compute_disk',
        'gcp_network': 'google_compute_network',
        'gcp_subnet': 'google_compute_subnetwork',
        'gcp_firewall': 'google_compute_firewall',
        'gcp_bucket': 'google_storage_bucket',
        
        # Short names for GCP
        'instance': 'google_compute_instance',
        'disk': 'google_compute_disk',
        'network': 'google_compute_network',
        'firewall': 'google_compute_firewall',
        'bucket': 'google_storage_bucket',
    }
    
    # Apply mappings based on provider
    if provider == "aws":
        return aws_mappings.get(resource_type, f"aws_{resource_type}")
    elif provider == "azure":
        return azure_mappings.get(resource_type, f"azurerm_{resource_type}")
    elif provider == "gcp":
        return gcp_mappings.get(resource_type, f"google_{resource_type}")
    else:
        # Default to AWS if provider detection fails
        return aws_mappings.get(resource_type, f"aws_{resource_type}")


def derive_resource_name(resource_type: str, resource: Dict[str, Any], remote_id: str) -> str:
    """Generate a Terraform-safe name based on provider and resource info."""
    provider = detect_provider_from_resource_type(resource_type)

    # Prefer precomputed sanitized names if available
    if isinstance(resource, dict):
        pre_sanitized = resource.get("name_sanitized") or resource.get("domain_sanitized")
        if pre_sanitized:
            return to_terraform_resource_name(pre_sanitized)

    base = str(remote_id)

    if provider == "aws":
        normalized_type = normalize_terraform_resource_type(resource_type, provider)

        if normalized_type == "aws_route53_record":
            # remote_id format: ZONEID_name_type[_setidentifier]
            if "_" in base:
                base = base.split("_", 1)[1]

        elif normalized_type == "aws_api_gateway_deployment":
            # remote_id format: restApiId/deploymentId
            if "/" in base:
                api_id, deploy_id = base.split("/", 1)
                base = f"{api_id}_deployment_{deploy_id}"
            else:
                base = strip_id_prefix(base)

        elif normalized_type == "aws_acm_certificate":
            domain = resource.get("DomainName") or resource.get("domain_name")
            if domain:
                base = f"certificate_{domain}"
            else:
                base = f"certificate_{strip_id_prefix(base)}"

        else:
            base = strip_id_prefix(base)

    elif provider in ("azure", "gcp"):
        base = resource.get("name") or base

    if "/" in base:
        base = base.replace("/", "_")

    return to_terraform_resource_name(base)


def generate_imports_file(
    resource_type: str,
    resources: List[Dict[str, Any]],
    remote_resource_id_key: str,
    output_dir: Path,
    composite_keys: Optional[List[str]] = None,
    provider: Optional[str] = None,
    provider_metadata: Optional[Dict[str, Any]] = None,
):
    """
    Generates a .json file containing the necessary data for terraform import commands.

    Args:
        resource_type: The resource type (can be short name like 'api_gateway_deployment' 
                      or full name like 'aws_api_gateway_deployment').
        resources: The list of resource dictionaries from the cloud provider API.
        remote_resource_id_key: The key in the resource dict that holds the unique ID.
        output_dir: The directory to save the file in.
        composite_keys (optional): A list of keys to join with '/' to form a composite ID,
                                   required for some resources like API Gateway methods.
        provider (optional): Cloud provider ('aws', 'azure', 'gcp'). Auto-detected if not provided.
        provider_metadata (optional): Additional metadata (e.g. account ID and region)
            associated with the scanned resources.
    """
    # Normalize the resource type to full Terraform resource type
    terraform_resource_type = normalize_terraform_resource_type(resource_type, provider)
    
    import_data = []
    for resource in resources:
        # Determine the remote ID for the 'terraform import' command.
        if composite_keys:
            # Build the ID from multiple keys, e.g., "api_id/resource_id/method".
            # This is necessary for many API Gateway resources.
            try:
                remote_id = "/".join([str(resource[key]) for key in composite_keys])
            except KeyError as e:
                print(f"Warning: Missing key {e} when building composite ID for a {terraform_resource_type}. Skipping.")
                continue
        else:
            remote_id = resource.get(remote_resource_id_key)

        if not remote_id:
            print(f"Warning: Could not determine remote ID for a {terraform_resource_type} using key '{remote_resource_id_key}'. Skipping.")
            continue

        # Create a sanitized, unique name for the resource in the Terraform state
        sanitized_name = derive_resource_name(resource_type, resource, remote_id)
        
        entry = {
            "resource_type": terraform_resource_type,  # Now uses full Terraform resource type
            "resource_name": sanitized_name,
            "remote_id": remote_id,
        }
        if provider_metadata is not None:
            entry["provider_metadata"] = provider_metadata

        import_data.append(entry)
    
    # Use the original resource_type for the filename to maintain compatibility
    base_resource_type = resource_type.replace('aws_', '').replace('azurerm_', '').replace('google_', '')
    import_file = output_dir / f"{base_resource_type}_import.json"
    
    try:
        with open(import_file, "w", encoding="utf-8") as f:
            json.dump(import_data, f, indent=2)
        print(f"Generated import file: {import_file} with {len(import_data)} resources")
    except IOError as e:
        print(f"Error writing import file {import_file}: {e}")


def read_import_file(import_file: Path) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Read and validate an import file.

    Returns:
        A tuple ``(entries, error)`` where ``entries`` is the list of import
        definitions and ``error`` contains any non JSON-decode related problem.

    Raises:
        ValueError: If the file contains invalid JSON.
    """

    try:
        with open(import_file, "r") as f:
            import_data = json.load(f)
    except json.JSONDecodeError as e:
        # Surface JSON errors to the caller so the filename can be reported
        raise ValueError(f"Invalid JSON: {e}") from e
    except IOError as e:
        return [], str(e)

    # Ensure all entries have proper resource types
    normalized_data: List[Dict[str, Any]] = []
    for entry in import_data:
        if isinstance(entry, dict):
            resource_type = entry.get("resource_type", "")
            normalized_type = normalize_terraform_resource_type(resource_type)

            normalized_entry = dict(entry)
            normalized_entry["resource_type"] = normalized_type
            normalized_data.append(normalized_entry)
        else:
            normalized_data.append(entry)

    return normalized_data, None


def validate_import_file(import_file: Path) -> List[str]:
    """
    Validate an import file for common issues.
    
    Returns:
        List of validation errors.
    """
    errors = []
    
    try:
        import_data, error = read_import_file(import_file)
        if error:
            errors.append(f"Failed to read file: {error}")
            return errors
    
        for i, entry in enumerate(import_data):
            if not isinstance(entry, dict):
                errors.append(f"Entry {i}: Not a dictionary")
                continue
            
            # Check required fields
            required_fields = ['resource_type', 'resource_name', 'remote_id']
            for field in required_fields:
                if field not in entry:
                    errors.append(f"Entry {i}: Missing required field '{field}'")
                elif not entry[field]:
                    errors.append(f"Entry {i}: Empty value for field '{field}'")
            
            # Validate resource type format
            resource_type = entry.get('resource_type', '')
            if resource_type and not any(resource_type.startswith(p) for p in ['aws_', 'azurerm_', 'google_']):
                errors.append(f"Entry {i}: Resource type '{resource_type}' should have provider prefix")
            
            # Validate resource name format (Terraform identifier rules)
            resource_name = entry.get('resource_name', '')
            if resource_name and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', resource_name):
                errors.append(f"Entry {i}: Invalid resource name '{resource_name}' (must match Terraform identifier rules)")
    
    except Exception as e:
        errors.append(f"Failed to validate file: {e}")
    
    return errors
