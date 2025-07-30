import pytest
from pathlib import Path
from terraback.utils.terraform_checker import (
    check_and_fix_terraform_files,
    TerraformChecker,
)


def test_check_and_fix_terraform_files_tmp(tmp_path: Path):
    # create a minimal terraform module
    module_dir = tmp_path / "tf"
    module_dir.mkdir()
    (module_dir / "main.tf").write_text("terraform {}\n")

    # ensure no TypeError is raised and result matches installation state
    result = check_and_fix_terraform_files(module_dir)
    if TerraformChecker.is_terraform_installed():
        assert result is True
    else:
        assert result is False
