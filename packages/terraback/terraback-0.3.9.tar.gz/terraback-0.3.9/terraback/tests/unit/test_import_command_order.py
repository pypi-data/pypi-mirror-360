import json
from unittest.mock import patch
from terraback.cli.main import import_all_resources


def test_import_command_places_options_first(tmp_path):
    # Create an import file with a single resource
    data = [
        {
            "resource_type": "aws_instance",
            "resource_name": "example",
            "remote_id": "i-abc123"
        }
    ]
    import_file = tmp_path / "sample_import.json"
    import_file.write_text(json.dumps(data))

    # Terraform directory containing a .terraform folder to skip init
    (tmp_path / ".terraform").mkdir()

    calls = []

    class Result:
        def __init__(self, returncode=0, stdout="", stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return Result()

    # Patch subprocess.run used inside the CLI function
    with patch("subprocess.run", side_effect=fake_run):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=1,
            validate=True,
            workflow="import",
        )

    expected = [
        "terraform",
        "import",
        "-lock-timeout=300s",
        "aws_instance.example",
        "i-abc123",
    ]
    assert expected in calls
