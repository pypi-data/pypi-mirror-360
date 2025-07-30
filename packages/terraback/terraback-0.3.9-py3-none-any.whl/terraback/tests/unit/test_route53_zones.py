import tempfile
from pathlib import Path

from terraback.terraform_generator.writer import generate_tf


def test_zone_template_generates_resource(tmp_path):
    zone = {
        "Name": "example.com.",
        "ZoneId": "Z123",
        "Config": {"Comment": "example", "PrivateZone": False},
        "VPCs": [],
        "Tags": [],
        "name_sanitized": "example_com",
    }

    output_file = tmp_path / "route53_zone.tf"
    generate_tf([zone], "route53_zone", output_file)

    content = output_file.read_text()
    assert 'resource "aws_route53_zone" "example_com"' in content
    assert 'name    = "example.com."' in content
