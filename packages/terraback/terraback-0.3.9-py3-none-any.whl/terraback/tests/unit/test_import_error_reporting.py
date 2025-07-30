import json
from unittest.mock import patch
import pytest
import typer
from terraback.cli.main import import_all_resources


def test_invalid_import_file_reports_filename(tmp_path, capsys):
    bad = tmp_path / "bad_import.json"
    bad.write_text("{bad json}")
    (tmp_path / ".terraform").mkdir()

    with patch("typer.confirm", return_value=False):
        with pytest.raises(typer.Exit):
            import_all_resources(
                output_dir=tmp_path,
                terraform_dir=tmp_path,
                dry_run=False,
                yes=True,
                parallel=1,
                validate=True,
                workflow="import",
            )

    captured = capsys.readouterr()
    assert "bad_import.json" in captured.out or "bad_import.json" in captured.err


def test_failed_import_includes_stderr(tmp_path, capsys):
    data = [
        {
            "resource_type": "aws_instance",
            "resource_name": "example",
            "remote_id": "i-abc123",
        }
    ]
    import_file = tmp_path / "sample_import.json"
    import_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    class Result:
        def __init__(self, returncode=0, stdout="", stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_run(cmd, **kwargs):
        if "import" in cmd:
            return Result(returncode=1, stderr="boom")
        return Result()

    with patch("subprocess.run", side_effect=fake_run):
        with pytest.raises(typer.Exit):
            import_all_resources(
                output_dir=tmp_path,
                terraform_dir=tmp_path,
                dry_run=False,
                yes=True,
                parallel=1,
                validate=True,
                workflow="import",
            )

    captured = capsys.readouterr()
    assert "sample_import.json" in captured.out
    assert "boom" in captured.out


def test_verify_flag_checks_account(tmp_path):
    data = [
        {
            "resource_type": "aws_instance",
            "resource_name": "example",
            "remote_id": "i-abc123",
            "provider_metadata": {"account_id": "111111111111", "region": "us-east-1"},
        }
    ]
    import_file = tmp_path / "sample_import.json"
    import_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    class FakeSession:
        region_name = "us-east-1"

        def client(self, service):
            class STS:
                def get_caller_identity(self_inner):
                    return {"Account": "222222222222"}

            return STS()

    with patch("terraback.cli.aws.session.get_boto_session", return_value=FakeSession()):
        with pytest.raises(typer.Exit):
            import_all_resources(
                output_dir=tmp_path,
                terraform_dir=tmp_path,
                dry_run=True,
                yes=True,
                parallel=1,
                validate=True,
                verify=True,
                workflow="import",
            )

