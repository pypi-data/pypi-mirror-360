#!/usr/bin/env python3
"""
Terraform Installation Checker for Terraback
Provides clear error messages when Terraform is not installed
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
import typer


class TerraformChecker:
    """Checks Terraform installation and provides helpful error messages."""
    
    @staticmethod
    def is_terraform_installed() -> bool:
        """Check if terraform command is available in PATH."""
        return shutil.which('terraform') is not None
    
    @staticmethod
    def get_terraform_version() -> Optional[str]:
        """Get terraform version if installed."""
        if not TerraformChecker.is_terraform_installed():
            return None
        
        try:
            result = subprocess.run(
                ['terraform', 'version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output like "Terraform v1.5.0"
                for line in result.stdout.split('\n'):
                    if 'Terraform v' in line:
                        return line.strip()
            return "Unknown version"
        except Exception:
            return None
    
    @staticmethod
    def check_terraform_required() -> bool:
        """
        Check if Terraform is installed and show helpful error if not.
        Returns True if Terraform is available, False otherwise.
        """
        if TerraformChecker.is_terraform_installed():
            version = TerraformChecker.get_terraform_version()
            if version:
                typer.echo(f"Found {version}")
            return True
        
        # Show helpful error message
        typer.echo()
        typer.secho("Terraform Not Found", fg="red", bold=True)
        typer.echo()
        typer.echo("Terraback requires Terraform to be installed and available in your PATH.")
        typer.echo()
        typer.secho("Installation Options:", fg="blue", bold=True)
        typer.echo()
        
        # Detection for different operating systems
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            typer.echo("macOS:")
            typer.echo("  brew tap hashicorp/tap")
            typer.echo("  brew install hashicorp/tap/terraform")
        elif system == "linux":
            typer.echo("Linux:")
            typer.echo("  # Ubuntu/Debian:")
            typer.echo("  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg")
            typer.echo("  sudo apt update && sudo apt install terraform")
            typer.echo()
            typer.echo("  # Or download from: https://www.terraform.io/downloads")
        elif system == "windows":
            typer.echo("Windows:")
            typer.echo("  # Using Chocolatey:")
            typer.echo("  choco install terraform")
            typer.echo()
            typer.echo("  # Or download from: https://www.terraform.io/downloads")
        else:
            typer.echo("Download from: https://www.terraform.io/downloads")
        
        typer.echo()
        typer.secho("Official Download:", fg="cyan")
        typer.echo("  https://www.terraform.io/downloads")
        typer.echo()
        typer.echo("After installation, make sure 'terraform' is available in your PATH.")
        typer.echo("Test with: terraform version")
        typer.echo()
        
        return False
    
    @staticmethod
    def safe_terraform_init(directory: Path) -> Tuple[bool, str]:
        """
        Safely run terraform init with proper error handling.
        Returns (success, error_message).
        """
        if not TerraformChecker.check_terraform_required():
            return False, "Terraform not installed"
        
        try:
            typer.echo(f"Initializing Terraform in {directory}...")
            result = subprocess.run(
                ['terraform', 'init'],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                typer.echo("Terraform initialization successful")
                return True, ""
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                typer.secho("Terraform init failed:", fg="red")
                typer.echo(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Terraform init timed out after 5 minutes"
            typer.secho(f"{error_msg}", fg="red")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error running terraform init: {e}"
            typer.secho(f"{error_msg}", fg="red")
            return False, error_msg
    
    @staticmethod
    def safe_terraform_validate(directory: Path) -> Tuple[bool, str]:
        """
        Safely run terraform validate with proper error handling.
        Returns (success, error_message).
        """
        if not TerraformChecker.check_terraform_required():
            return False, "Terraform not installed"
        
        try:
            result = subprocess.run(
                ['terraform', 'validate'],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                typer.echo("Terraform validation successful")
                return True, ""
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                typer.secho("Terraform validation failed:", fg="red")
                typer.echo(error_msg)
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Terraform validate timed out"
            typer.secho(f"{error_msg}", fg="red")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error running terraform validate: {e}"
            typer.secho(f"{error_msg}", fg="red")
            return False, error_msg
    
    @staticmethod
    def safe_terraform_fmt(directory: Path) -> Tuple[bool, str]:
        """
        Safely run terraform fmt with proper error handling.
        Returns (success, error_message).
        """
        if not TerraformChecker.is_terraform_installed():
            typer.echo("Warning: Terraform not found. Skipping formatting.")
            return False, "Terraform not installed"
        
        try:
            result = subprocess.run(
                ['terraform', 'fmt'],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                typer.echo("Terraform formatting successful")
                return True, ""
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                typer.echo(f"Warning: terraform fmt had issues: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Terraform fmt timed out"
            typer.echo(f"Warning: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Could not run terraform fmt: {e}"
            typer.echo(f"Warning: {error_msg}")
            return False, error_msg


def check_and_fix_terraform_files(output_dir: Path) -> bool:
    """
    Check Terraform installation and fix/validate generated files.
    Returns True if everything is successful.
    """
    from template_syntax_fixer import TerraformSyntaxFixer, run_terraform_fmt
    
    # First, fix syntax issues
    typer.echo("Fixing Terraform syntax issues...")
    fixer = TerraformSyntaxFixer(output_dir)
    fixed_files = fixer.fix_all_files()
    
    if fixed_files:
        typer.echo(f"Fixed {len(fixed_files)} files")
    
    # Check if Terraform is installed
    if not TerraformChecker.check_terraform_required():
        typer.echo()
        typer.secho("Cannot validate Terraform files without Terraform installed.", fg="yellow")
        typer.echo("Files have been generated and syntax-fixed, but you'll need to install")
        typer.echo("Terraform to run 'terraform init', 'terraform validate', etc.")
        return False
    
    # Format files
    typer.echo("Formatting Terraform files...")
    success, error = TerraformChecker.safe_terraform_fmt(output_dir)
    
    # Initialize and validate
    typer.echo("Initializing Terraform...")
    init_success, init_error = TerraformChecker.safe_terraform_init(output_dir)
    
    if init_success:
        typer.echo("Validating Terraform configuration...")
        validate_success, validate_error = TerraformChecker.safe_terraform_validate(output_dir)
        
        if validate_success:
            typer.echo()
            typer.secho("All Terraform files are valid and ready to use!", fg="green", bold=True)
            typer.echo()
            typer.echo("Next steps:")
            typer.echo("  terraform plan    # Review what will be imported")
            typer.echo("  terraback import-all --parallel=8    # Import all resources")
            return True
        else:
            typer.echo()
            typer.secho("Terraform validation failed. Please fix the issues above.", fg="red")
            return False
    else:
        typer.echo()
        typer.secho("Terraform initialization failed. Please fix the issues above.", fg="red")
        return False


def main():
    """Command line interface for the checker."""
    if len(sys.argv) != 2:
        print("Usage: python terraform_checker.py <output_directory>")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    if not output_dir.exists():
        print(f"Error: Directory {output_dir} does not exist")
        sys.exit(1)
    
    success = check_and_fix_terraform_files(output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
