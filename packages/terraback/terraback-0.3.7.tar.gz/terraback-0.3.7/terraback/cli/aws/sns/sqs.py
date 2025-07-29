
from pathlib import Path
from .queues import scan_queues, list_queues, import_queue
from .dead_letter_queues import scan_dlq, list_dlq, import_dlq

def scan_sqs_queues(output_dir: Path, profile: str = None, region: str = "us-east-1", include_fifo: bool = True, include_dlq: bool = True):
    """
    Wrapper function to scan SQS queues and generate Terraform code.
    
    Args:
        output_dir: Directory to save Terraform files
        profile: AWS CLI profile to use
        region: AWS region
        include_fifo: Include FIFO queues (unused in current implementation, kept for API compatibility)
        include_dlq: Include Dead Letter Queues
    """
    # Scan regular queues
    scan_queues(output_dir, profile, region, include_dlq)
    
    # Also scan DLQ relationships if requested
    if include_dlq:
        scan_dlq(output_dir, profile, region)

def list_sqs_queues(output_dir: Path):
    """
    Wrapper function to list all SQS queue resources previously generated.
    
    Args:
        output_dir: Directory containing generated Terraform files
    """
    print("=== SQS Queues ===")
    list_queues(output_dir)
    print("\n=== DLQ Relationships ===")
    list_dlq(output_dir)

def import_sqs_queue(queue_url: str, output_dir: Path):
    """
    Wrapper function to run terraform import for a specific SQS queue by its URL.
    
    Args:
        queue_url: The SQS queue URL to import
        output_dir: Directory containing Terraform files
    """
    return import_queue(queue_url, output_dir)

# Additional DLQ-specific functions for advanced usage
def scan_sqs_dlq_relationships(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Dedicated function to scan only DLQ relationships.
    
    Args:
        output_dir: Directory to save Terraform files
        profile: AWS CLI profile to use
        region: AWS region
    """
    return scan_dlq(output_dir, profile, region)

def list_sqs_dlq_relationships(output_dir: Path):
    """
    List only DLQ relationship resources.
    
    Args:
        output_dir: Directory containing generated Terraform files
    """
    return list_dlq(output_dir)

def import_sqs_dlq_relationship(relationship_id: str, output_dir: Path):
    """
    Import a specific DLQ relationship.
    
    Args:
        relationship_id: The DLQ relationship ID to import
        output_dir: Directory containing Terraform files
    """
    return import_dlq(relationship_id, output_dir)