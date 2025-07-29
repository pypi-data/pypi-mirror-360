import os
import boto3
import pytest
from moto import mock_aws
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

# Important: We need to set dummy AWS credentials for moto to work
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1" # Set a default region

# Now we can import the code we want to test
from cli.aws.vpc.vpcs import scan_vpcs
from utils.cross_scan_registry import CrossScanRegistry

@pytest.fixture
def ec2_client():
    """Pytest fixture to create a mocked EC2 client."""
    with mock_aws():
        yield boto3.client("ec2", region_name="us-east-1")

@mock_aws
def test_scan_vpcs_identifies_and_writes_vpc():
    """
    Integration test for the scan_vpcs function.
    It checks if the function correctly identifies a VPC in a mocked AWS
    environment and calls the writer with the correct details.
    """
    # 1. SETUP: Create a mock VPC in our fake AWS environment
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    vpc = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
    vpc_id = vpc["Vpc"]["VpcId"]
    ec2_client.create_tags(
        Resources=[vpc_id],
        Tags=[{'Key': 'Name', 'Value': 'test-vpc-name'}]
    )

    # 2. SETUP: Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        # Create registry and mock writer
        registry = CrossScanRegistry()
        mock_writer = MagicMock()

        # 3. EXECUTE: Run the function we are testing
        # Mock the get_boto_session to return our mocked session
        with patch('cli.aws.vpc.vpcs.get_boto_session') as mock_get_session:
            mock_session = MagicMock()
            mock_session.client.return_value = ec2_client
            mock_get_session.return_value = mock_session
            
            # Call with the correct parameters based on the actual function signature
            scan_vpcs(output_dir, mock_writer)

        # 4. ASSERT: Check if the results are what we expect
        # Check if vpc.tf file was created
        vpc_file = output_dir / "vpc.tf"
        assert vpc_file.exists(), "vpc.tf file should be created"
        
        # Read the content and verify it contains our VPC
        content = vpc_file.read_text()
        print(f"Generated content:\n{content}")  # Debug output
        
        # The VPC ID appears in the resource name as vpc_vpc_{id_without_dashes}
        vpc_id_clean = vpc_id.replace('vpc-', '').replace('-', '')  # Remove vpc- prefix and all dashes
        expected_resource_name = f"vpc_vpc_{vpc_id_clean}"
        assert expected_resource_name in content, f"Expected resource name {expected_resource_name} should be in terraform file"
        assert "test-vpc-name" in content, "VPC name should be in the generated terraform file"
        assert "10.0.0.0/16" in content, "VPC CIDR block should be in the generated terraform file"