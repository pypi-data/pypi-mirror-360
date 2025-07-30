from unittest.mock import patch

import pytest
import typer
from terraback.import_workflows import import_with_blocks


def _fake_result(returncode=0, stdout="", stderr=""):
    class Result:
        def __init__(self):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    return Result()


def test_runs_init_when_missing(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _fake_result()

    with patch("subprocess.run", side_effect=fake_run):
        import_with_blocks(tmp_path, resources)

    assert ["terraform", "init"] in calls
    assert ["terraform", "plan", "-generate-config-out=import.plan"] in calls
    assert ["terraform", "apply", "import.plan"] in calls


def test_skips_init_when_present(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _fake_result()

    with patch("subprocess.run", side_effect=fake_run):
        import_with_blocks(tmp_path, resources)

    assert ["terraform", "init"] not in calls
    assert ["terraform", "plan", "-generate-config-out=import.plan"] in calls
    assert ["terraform", "apply", "import.plan"] in calls


def test_plan_failure_exits(tmp_path):
    resources = [{"type": "aws_instance", "name": "example", "id": "i-1"}]
    (tmp_path / ".terraform").mkdir()
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "plan" in cmd:
            return _fake_result(returncode=1, stderr="failed plan")
        return _fake_result()

    with patch("subprocess.run", side_effect=fake_run):
        with pytest.raises(typer.Exit):
            import_with_blocks(tmp_path, resources)

    assert ["terraform", "init"] not in calls
    assert ["terraform", "plan", "-generate-config-out=import.plan"] in calls
