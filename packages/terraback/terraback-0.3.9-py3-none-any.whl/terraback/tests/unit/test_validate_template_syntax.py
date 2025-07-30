import pytest
from terraback.terraform_generator import writer


def test_validate_existing_template():
    """Valid templates should return no syntax errors."""
    writer.reset_template_loader()
    writer.AutoDiscoveryTemplateLoader._instance = None
    loader = writer.get_template_loader()

    errors = loader.validate_template_syntax("s3_bucket", provider="aws")
    assert errors == []


def test_validate_malformed_template(tmp_path):
    """Malformed templates should produce syntax errors."""
    template_dir = tmp_path / "templates"
    aws_dir = template_dir / "aws"
    aws_dir.mkdir(parents=True)

    # Create a template with invalid Jinja syntax
    bad_template = aws_dir / "bad_template.tf.j2"
    bad_template.write_text("{% if foo %}\nresource \"aws_s3_bucket\" \"test\" {}\n")

    writer.AutoDiscoveryTemplateLoader._instance = None
    loader = writer.AutoDiscoveryTemplateLoader(template_dir_override=template_dir)

    errors = loader.validate_template_syntax("bad_template", provider="aws")
    assert errors  # Expect at least one error reported

