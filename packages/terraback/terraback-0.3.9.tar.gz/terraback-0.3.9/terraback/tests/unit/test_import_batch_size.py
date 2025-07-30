import json
import pytest
import typer
from terraback.cli.main import import_all_resources


def test_invalid_batch_size(tmp_path, capsys):
    data = [
        {"resource_type": "aws_instance", "resource_name": "example", "remote_id": "i-123"}
    ]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    with pytest.raises(typer.Exit):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=True,
            yes=True,
            parallel=1,
            validate=True,
            workflow="workspaces",
            batch_size=0,
        )

    captured = capsys.readouterr()
    assert "batch-size" in captured.err
