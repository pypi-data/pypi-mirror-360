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

from terraback.utils.logging import get_logger
logger = get_logger(__name__)

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
                logger.info(f"Found {version}")
            return True
        
        # Show helpful error message
        logger.info("")
        typer.secho("Terraform Not Found", fg="red", bold=True)
        logger.info("")
        logger.info("Terraback requires Terraform to be installed and available in your PATH.")
        logger.info("")
        typer.secho("Installation Options:", fg="blue", bold=True)
        logger.info("")
        
        # Detection for different operating systems
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            logger.info("macOS:")
            logger.info("  brew tap hashicorp/tap")
            logger.info("  brew install hashicorp/tap/terraform")
        elif system == "linux":
            logger.info("Linux:")
            logger.info("  # Ubuntu/Debian:")
            logger.info("  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg")
            logger.info("  sudo apt update && sudo apt install terraform")
            logger.info("")
            logger.info("  # Or download from: https://www.terraform.io/downloads")
        elif system == "windows":
            logger.info("Windows:")
            logger.info("  # Using Chocolatey:")
            logger.info("  choco install terraform")
            logger.info("")
            logger.info("  # Or download from: https://www.terraform.io/downloads")
        else:
            logger.info("Download from: https://www.terraform.io/downloads")
        
        logger.info("")
        typer.secho("Official Download:", fg="cyan")
        logger.info("  https://www.terraform.io/downloads")
        logger.info("")
        logger.info("After installation, make sure 'terraform' is available in your PATH.")
        logger.info("Test with: terraform version")
        logger.info("")
        
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
            logger.info(f"Initializing Terraform in {directory}...")
            result = subprocess.run(
                ['terraform', 'init'],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Terraform initialization successful")
                return True, ""
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                typer.secho("Terraform init failed:", fg="red")
                logger.info(error_msg)
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
                logger.info("Terraform validation successful")
                return True, ""
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                typer.secho("Terraform validation failed:", fg="red")
                logger.info(error_msg)
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
            logger.info("Warning: Terraform not found. Skipping formatting.")
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
                logger.info("Terraform formatting successful")
                return True, ""
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                logger.info(f"Warning: terraform fmt had issues: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "Terraform fmt timed out"
            logger.info(f"Warning: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Could not run terraform fmt: {e}"
            logger.info(f"Warning: {error_msg}")
            return False, error_msg


def check_and_fix_terraform_files(output_dir: Path) -> bool:
    """
    Check Terraform installation and fix/validate generated files.
    Returns True if everything is successful.
    """
    from terraback.utils.template_syntax_fixer import (
        TerraformSyntaxFixer,
        run_terraform_fmt,
    )
    
    # First, fix syntax issues
    logger.info("Fixing Terraform syntax issues...")
    fixer = TerraformSyntaxFixer(output_dir)
    fixed_files = fixer.fix_all_files()
    
    if fixed_files:
        logger.info(f"Fixed {len(fixed_files)} files")
    
    # Check if Terraform is installed
    if not TerraformChecker.check_terraform_required():
        logger.info("")
        typer.secho("Cannot validate Terraform files without Terraform installed.", fg="yellow")
        logger.info("Files have been generated and syntax-fixed, but you'll need to install")
        logger.info("Terraform to run 'terraform init', 'terraform validate', etc.")
        return False
    
    # Format files
    logger.info("Formatting Terraform files...")
    success, error = TerraformChecker.safe_terraform_fmt(output_dir)
    
    # Initialize and validate
    logger.info("Initializing Terraform...")
    init_success, init_error = TerraformChecker.safe_terraform_init(output_dir)
    
    if init_success:
        logger.info("Validating Terraform configuration...")
        validate_success, validate_error = TerraformChecker.safe_terraform_validate(output_dir)
        
        if validate_success:
            logger.info("")
            typer.secho("All Terraform files are valid and ready to use!", fg="green", bold=True)
            logger.info("")
            logger.info("Next steps:")
            logger.info("  terraform plan    # Review what will be imported")
            logger.info("  terraback import-all --parallel=8    # Import all resources")
            return True
        else:
            logger.info("")
            typer.secho("Terraform validation failed. Please fix the issues above.", fg="red")
            return False
    else:
        logger.info("")
        typer.secho("Terraform initialization failed. Please fix the issues above.", fg="red")
        return False


def main():
    """Command line interface for the checker."""
    if len(sys.argv) != 2:
        logger.info("Usage: python terraform_checker.py <output_directory>")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    if not output_dir.exists():
        logger.error("Directory %s does not exist", output_dir)
        sys.exit(1)
    
    success = check_and_fix_terraform_files(output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
