import json
from unittest.mock import patch

import typer
from terraback.cli.main import import_all_resources


async def _fake_create_subprocess_exec(*cmd, **kwargs):
    class Proc:
        returncode = 0

        async def communicate(self):
            return b"", b""

    return Proc()


class DummyProgressBar:
    def __init__(self):
        self.updates = []

    def update(self, n):
        self.updates.append(n)


class DummyProgress:
    def __init__(self, bar):
        self.bar = bar

    def __enter__(self):
        return self.bar

    def __exit__(self, exc_type, exc, tb):
        pass


def test_async_import_with_progress(tmp_path):
    data = [
        {"resource_type": "aws_instance", "resource_name": "one", "remote_id": "i-1"},
        {"resource_type": "aws_instance", "resource_name": "two", "remote_id": "i-2"},
    ]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    bar = DummyProgressBar()

    def fake_progressbar(length, label=""):
        assert length == len(data)
        return DummyProgress(bar)

    with (
        patch("asyncio.create_subprocess_exec", side_effect=_fake_create_subprocess_exec) as proc_patch,
        patch("subprocess.run", side_effect=AssertionError("subprocess.run should not be called")),
        patch("sys.stdout.isatty", return_value=True),
        patch("typer.progressbar", side_effect=fake_progressbar),
        patch("typer.echo")  # silence output
    ):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=2,
            validate=True,
            async_mode=True,
            progress=True,
            workflow="import",
        )

    assert proc_patch.call_count == 2
    assert bar.updates == [1, 1]


def test_async_import_no_progress(tmp_path):
    data = [
        {"resource_type": "aws_instance", "resource_name": "only", "remote_id": "i-3"}
    ]
    imp_file = tmp_path / "sample_import.json"
    imp_file.write_text(json.dumps(data))
    (tmp_path / ".terraform").mkdir()

    progress_called = False

    def fake_progressbar(*args, **kwargs):
        nonlocal progress_called
        progress_called = True
        return DummyProgress(DummyProgressBar())

    with (
        patch("asyncio.create_subprocess_exec", side_effect=_fake_create_subprocess_exec),
        patch("subprocess.run", side_effect=AssertionError("subprocess.run should not be called")),
        patch("sys.stdout.isatty", return_value=True),
        patch("typer.progressbar", side_effect=fake_progressbar),
        patch("typer.echo")
    ):
        import_all_resources(
            output_dir=tmp_path,
            terraform_dir=tmp_path,
            dry_run=False,
            yes=True,
            parallel=1,
            validate=True,
            async_mode=True,
            progress=False,
            workflow="import",
        )

    assert not progress_called
