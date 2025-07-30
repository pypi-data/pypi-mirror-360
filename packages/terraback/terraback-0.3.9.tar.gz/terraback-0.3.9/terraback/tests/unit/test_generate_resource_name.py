import json
from pathlib import Path
from terraback.terraform_generator.imports import generate_imports_file


def test_composite_id_sanitization(tmp_path: Path):
    resources = [{"id": "jaejtnxq15/2e8yv2/POST"}]
    generate_imports_file(
        "aws_api_gateway_method",
        resources,
        remote_resource_id_key="id",
        output_dir=tmp_path,
    )
    import_file = tmp_path / "api_gateway_method_import.json"
    data = json.loads(import_file.read_text())
    assert data[0]["resource_name"] == "jaejtnxq15_2e8yv2_post"


def test_apigw_deployment_name(tmp_path: Path):
    resources = [{"id": "api123/def456"}]
    generate_imports_file(
        "aws_api_gateway_deployment",
        resources,
        remote_resource_id_key="id",
        output_dir=tmp_path,
    )
    import_file = tmp_path / "api_gateway_deployment_import.json"
    data = json.loads(import_file.read_text())
    assert data[0]["resource_name"] == "api123_deployment_def456"


def test_route53_record_name(tmp_path: Path):
    resources = [{
        "ImportId": "Z12345_example.com._A",
        "ZoneId": "Z12345",
        "Name": "example.com.",
        "Type": "A",
    }]
    generate_imports_file(
        "aws_route53_record",
        resources,
        remote_resource_id_key="ImportId",
        output_dir=tmp_path,
    )
    import_file = tmp_path / "route53_record_import.json"
    data = json.loads(import_file.read_text())
    assert data[0]["resource_name"] == "example_com_a"


def test_acm_certificate_name(tmp_path: Path):
    resources = [{
        "CertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/abcde",
        "DomainName": "example.com"
    }]
    generate_imports_file(
        "aws_acm_certificate",
        resources,
        remote_resource_id_key="CertificateArn",
        output_dir=tmp_path,
    )
    import_file = tmp_path / "acm_certificate_import.json"
    data = json.loads(import_file.read_text())
    assert data[0]["resource_name"] == "certificate_example_com"


def test_reuse_name_sanitized(tmp_path: Path):
    resources = [{"ZoneId": "Z1", "name_sanitized": "123foo"}]
    generate_imports_file(
        "route53_zone",
        resources,
        remote_resource_id_key="ZoneId",
        output_dir=tmp_path,
    )
    import_file = tmp_path / "route53_zone_import.json"
    data = json.loads(import_file.read_text())
    assert data[0]["resource_name"] == "resource_123foo"


def test_provider_metadata_included(tmp_path: Path):
    resources = [{"id": "i-123"}]
    generate_imports_file(
        "aws_instance",
        resources,
        remote_resource_id_key="id",
        output_dir=tmp_path,
        provider_metadata={"account_id": "111111111111", "region": "us-east-1"},
    )
    import_file = tmp_path / "instance_import.json"
    data = json.loads(import_file.read_text())
    assert data[0]["provider_metadata"]["account_id"] == "111111111111"
