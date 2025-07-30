import pytest
from terraback.cli.main import _ensure_resource_blocks


def test_route53_record_stub_has_records_and_ttl(tmp_path):
    resources = [
        {
            "type": "aws_route53_record",
            "name": "test",
            "id": "Z1234_test",
        }
    ]

    _ensure_resource_blocks(tmp_path, resources)

    stub_file = tmp_path / "terraback_import_stubs.tf"
    assert stub_file.exists()
    content = stub_file.read_text()
    assert 'records = ["127.0.0.1"]' in content
    assert 'ttl = 300' in content
