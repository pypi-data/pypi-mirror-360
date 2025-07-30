import pytest
from terraback.terraform_generator import writer


def test_add_helper_fields_no_exception():
    # Ensure a fresh loader instance
    writer.reset_template_loader()
    writer.AutoDiscoveryTemplateLoader._instance = None
    loader = writer.get_template_loader()

    resource = {
        "InstanceId": "i-abcdef123456",
        "ArnField": "arn:aws:ec2:us-east-1:123456789012:instance/i-abcdef123456",
        "Tags": [{"Key": "Name", "Value": "example"}],
    }

    loader._add_helper_fields(resource, "ec2_instance")

    assert resource["ArnField_region"] == "us-east-1"
    assert resource["ArnField_account"] == "123456789012"
    assert "InstanceId_short" in resource
    assert resource["tags_formatted"]["Name"] == "example"
