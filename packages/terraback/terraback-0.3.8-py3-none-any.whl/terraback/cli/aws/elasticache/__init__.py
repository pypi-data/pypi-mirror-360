from terraback.core.license import require_professional
import typer
from pathlib import Path

from .redis_clusters import scan_redis_clusters, list_redis_clusters, import_redis_cluster
from .memcached_clusters import scan_memcached_clusters, list_memcached_clusters, import_memcached_cluster
from .subnet_groups import scan_subnet_groups, list_subnet_groups, import_subnet_group
from .parameter_groups import scan_parameter_groups, list_parameter_groups, import_parameter_group
from .replication_groups import scan_replication_groups, list_replication_groups, import_replication_group

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="elasticache",
    help="Manage ElastiCache resources like Redis clusters, Memcached clusters, and configuration groups.",
    no_args_is_help=True
)

# --- Redis Cluster Commands ---
@app.command(name="scan-redis", help="Scan ElastiCache Redis clusters.")
@require_professional
def scan_redis_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_redis_clusters(output_dir, profile, region)

@app.command(name="list-redis", help="List scanned Redis clusters.")
@require_professional
def list_redis_command(output_dir: Path = typer.Option("generated")):
    list_redis_clusters(output_dir)

@app.command(name="import-redis", help="Import a Redis cluster by ID.")
@require_professional
def import_redis_command(
    cluster_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_redis_cluster(cluster_id, output_dir)

# --- Redis Replication Group Commands ---
@app.command(name="scan-replication-groups", help="Scan ElastiCache Redis replication groups.")
@require_professional
def scan_replication_groups_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_replication_groups(output_dir, profile, region)

@app.command(name="list-replication-groups", help="List scanned Redis replication groups.")
@require_professional
def list_replication_groups_command(output_dir: Path = typer.Option("generated")):
    list_replication_groups(output_dir)

@app.command(name="import-replication-group", help="Import a Redis replication group by ID.")
@require_professional
def import_replication_group_command(
    replication_group_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_replication_group(replication_group_id, output_dir)

# --- Memcached Cluster Commands ---
@app.command(name="scan-memcached", help="Scan ElastiCache Memcached clusters.")
@require_professional
def scan_memcached_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_memcached_clusters(output_dir, profile, region)

@app.command(name="list-memcached", help="List scanned Memcached clusters.")
@require_professional
def list_memcached_command(output_dir: Path = typer.Option("generated")):
    list_memcached_clusters(output_dir)

@app.command(name="import-memcached", help="Import a Memcached cluster by ID.")
@require_professional
def import_memcached_command(
    cluster_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_memcached_cluster(cluster_id, output_dir)

# --- Subnet Group Commands ---
@app.command(name="scan-subnet-groups", help="Scan ElastiCache subnet groups.")
@require_professional
def scan_subnet_groups_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_subnet_groups(output_dir, profile, region)

@app.command(name="list-subnet-groups", help="List scanned subnet groups.")
@require_professional
def list_subnet_groups_command(output_dir: Path = typer.Option("generated")):
    list_subnet_groups(output_dir)

@app.command(name="import-subnet-group", help="Import a subnet group by name.")
@require_professional
def import_subnet_group_command(
    subnet_group_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_subnet_group(subnet_group_name, output_dir)

# --- Parameter Group Commands ---
@app.command(name="scan-parameter-groups", help="Scan ElastiCache parameter groups.")
@require_professional
def scan_parameter_groups_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    family: str = typer.Option(None, help="Filter by parameter group family (redis6.x, memcached1.6)")
):
    scan_parameter_groups(output_dir, profile, region, family)

@app.command(name="list-parameter-groups", help="List scanned parameter groups.")
@require_professional
def list_parameter_groups_command(output_dir: Path = typer.Option("generated")):
    list_parameter_groups(output_dir)

@app.command(name="import-parameter-group", help="Import a parameter group by name.")
@require_professional
def import_parameter_group_command(
    parameter_group_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_parameter_group(parameter_group_name, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all ElastiCache resources.")
@require_professional
def scan_all_elasticache_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_subnet_groups(output_dir, profile, region)
    scan_parameter_groups(output_dir, profile, region)
    scan_replication_groups(output_dir, profile, region)
    scan_redis_clusters(output_dir, profile, region)
    scan_memcached_clusters(output_dir, profile, region)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the ElastiCache module."""
    register_scan_function("elasticache_redis_cluster", scan_redis_clusters)
    register_scan_function("elasticache_memcached_cluster", scan_memcached_clusters)
    register_scan_function("elasticache_replication_group", scan_replication_groups)
    register_scan_function("elasticache_subnet_group", scan_subnet_groups)
    register_scan_function("elasticache_parameter_group", scan_parameter_groups)

    # Define ElastiCache dependencies
    # Clusters depend on subnet groups and parameter groups
    cross_scan_registry.register_dependency("elasticache_redis_cluster", "elasticache_subnet_group")
    cross_scan_registry.register_dependency("elasticache_redis_cluster", "elasticache_parameter_group")
    cross_scan_registry.register_dependency("elasticache_memcached_cluster", "elasticache_subnet_group")
    cross_scan_registry.register_dependency("elasticache_memcached_cluster", "elasticache_parameter_group")
    cross_scan_registry.register_dependency("elasticache_replication_group", "elasticache_subnet_group")
    cross_scan_registry.register_dependency("elasticache_replication_group", "elasticache_parameter_group")
    
    # Clusters depend on VPC networking
    cross_scan_registry.register_dependency("elasticache_redis_cluster", "subnets")
    cross_scan_registry.register_dependency("elasticache_redis_cluster", "security_groups")
    cross_scan_registry.register_dependency("elasticache_memcached_cluster", "subnets")
    cross_scan_registry.register_dependency("elasticache_memcached_cluster", "security_groups")
    cross_scan_registry.register_dependency("elasticache_replication_group", "subnets")
    cross_scan_registry.register_dependency("elasticache_replication_group", "security_groups")
    
    # Subnet groups depend on VPC subnets
    cross_scan_registry.register_dependency("elasticache_subnet_group", "subnets")