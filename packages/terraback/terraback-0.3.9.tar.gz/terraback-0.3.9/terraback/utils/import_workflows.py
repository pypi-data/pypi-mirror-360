from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import typer


# Shared helpers for importing Terraform state using different workflows.

def import_with_blocks(terraform_dir: Path, resources: List[Dict[str, Any]]) -> None:
    """Write import blocks and apply them using Terraform."""
    import_file = terraform_dir / "terraback_import_blocks.tf"
    blocks: List[str] = []
    for imp in resources:
        rtype = imp.get("type") or imp.get("resource_type")
        rname = imp.get("name") or imp.get("resource_name")
        rid = imp.get("id") or imp.get("remote_id")
        if not (rtype and rname and rid):
            continue
        blocks.append(f"import {{\n  to = {rtype}.{rname}\n  id = \"{rid}\"\n}}\n")

    if blocks:
        import_file.write_text("\n".join(blocks), encoding="utf-8")

    if not (terraform_dir / ".terraform").exists():
        result = subprocess.run(
            ["terraform", "init"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            typer.secho("terraform init failed", fg="red")
            typer.secho(result.stderr or result.stdout)
            raise typer.Exit(1)

    result = subprocess.run(
        ["terraform", "plan", "-generate-config-out=import.plan"],
        cwd=terraform_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        typer.secho("terraform plan failed", fg="red")
        typer.secho(result.stderr or result.stdout)
        raise typer.Exit(1)
    result = subprocess.run(
        ["terraform", "apply", "import.plan"],
        cwd=terraform_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        typer.secho("terraform apply failed", fg="red")
        typer.secho(result.stderr or result.stdout)
        raise typer.Exit(1)


def _import_single_resource(terraform_dir: Path, imp: Dict[str, Any]) -> Dict[str, Any]:
    cmd = [
        "terraform",
        "import",
        "-lock-timeout=300s",
        imp["address"],
        imp["id"],
    ]
    result = subprocess.run(cmd, cwd=str(terraform_dir), capture_output=True, text=True)
    return {
        "imp": imp,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "file": imp.get("file"),
    }


async def _async_import_single_resource(terraform_dir: Path, imp: Dict[str, Any]) -> Dict[str, Any]:
    cmd = [
        "terraform",
        "import",
        "-lock-timeout=300s",
        imp["address"],
        imp["id"],
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(terraform_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {
        "imp": imp,
        "success": proc.returncode == 0,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "file": imp.get("file"),
    }


def import_with_commands(
    terraform_dir: Path,
    resources: Iterable[Dict[str, Any]],
    *,
    parallel: int = 1,
    async_mode: bool = False,
    progress: bool = True,
) -> Tuple[int, int, List[Dict[str, Any]]]:
    """Import resources using ``terraform import`` commands."""

    imported = 0
    failed = 0
    failed_imports: List[Dict[str, Any]] = []

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import sys
    import platform
    import typer

    progress_enabled = progress and sys.stdout.isatty()

    windows_old_python = platform.system() == "Windows" and sys.version_info < (3, 8)
    if async_mode and windows_old_python:
        typer.echo("Async mode not supported on this Windows Python version. Falling back to threads.")
        async_mode = False

    def handle_result(result: Dict[str, Any]) -> None:
        nonlocal imported, failed
        if result["success"]:
            imported += 1
            typer.echo(f"✓ {result['imp']['address']}")
        else:
            failed += 1
            failed_imports.append(result)
            typer.echo(f"✗ {result['imp']['address']}")
            if result["stderr"]:
                stderr = result["stderr"].strip()
                if "does not exist in the configuration" in stderr:
                    typer.echo("  Error: Resource definition missing in .tf files")
                elif "Cannot import non-existent remote object" in stderr:
                    typer.echo("  Error: Resource no longer exists in cloud provider")
                elif "already managed by Terraform" in stderr:
                    typer.echo("  Error: Resource already imported")
                else:
                    typer.echo(f"  Error: {stderr}")

    if async_mode:
        async def run_async():
            sem = asyncio.Semaphore(parallel)
            tasks = []

            async def sem_task(imp: Dict[str, Any]):
                async with sem:
                    return await _async_import_single_resource(terraform_dir, imp)

            for imp in resources:
                tasks.append(asyncio.create_task(sem_task(imp)))

            results: List[Dict[str, Any]] = []
            if progress_enabled:
                with typer.progressbar(length=len(tasks), label="Importing resources") as bar:
                    for coro in asyncio.as_completed(tasks):
                        res = await coro
                        bar.update(1)
                        results.append(res)
            else:
                for coro in asyncio.as_completed(tasks):
                    res = await coro
                    results.append(res)
            return results

        results = asyncio.run(run_async())
        for res in results:
            handle_result(res)
    else:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_import = {
                executor.submit(_import_single_resource, terraform_dir, imp): imp
                for imp in resources
            }
            if progress_enabled:
                with typer.progressbar(length=len(future_to_import), label="Importing resources") as bar:
                    for future in as_completed(future_to_import):
                        result = future.result()
                        bar.update(1)
                        handle_result(result)
            else:
                for future in as_completed(future_to_import):
                    result = future.result()
                    handle_result(result)

    return imported, failed, failed_imports


def import_with_workspaces(terraform_dir: Path, resources: Iterable[Dict[str, Any]]) -> None:
    """Import resources using separate Terraform workspaces."""
    for idx, imp in enumerate(resources):
        ws_name = f"tb{idx}"
        result = subprocess.run(
            ["terraform", "workspace", "new", ws_name],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            typer.secho(f"terraform workspace new {ws_name} failed", fg="red")
            typer.secho(result.stderr or result.stdout)
            raise typer.Exit(1)

        result = subprocess.run(
            ["terraform", "workspace", "select", ws_name],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            typer.secho(f"terraform workspace select {ws_name} failed", fg="red")
            typer.secho(result.stderr or result.stdout)
            raise typer.Exit(1)

        result = subprocess.run(
            [
                "terraform",
                "import",
                "-lock-timeout=300s",
                imp["address"],
                imp["id"],
            ],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            typer.secho(f"terraform import {imp['address']} failed", fg="red")
            typer.secho(result.stderr or result.stdout)
            raise typer.Exit(1)

        result = subprocess.run(
            ["terraform", "workspace", "select", "default"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            typer.secho("terraform workspace select default failed", fg="red")
            typer.secho(result.stderr or result.stdout)
            raise typer.Exit(1)

        result = subprocess.run(
            ["terraform", "workspace", "delete", ws_name],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            typer.secho(f"terraform workspace delete {ws_name} failed", fg="red")
            typer.secho(result.stderr or result.stdout)
            raise typer.Exit(1)

