#!/usr/bin/env python3
"""
Terraform Template Syntax Fixer for Terraback
Fixes common syntax issues in generated Terraform files
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class TerraformSyntaxFixer:
    """Fixes common Terraform syntax issues in generated files."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.fixes_applied = []
    
    def fix_all_files(self) -> List[str]:
        """Fix all .tf files in the output directory."""
        tf_files = list(self.output_dir.glob("*.tf"))
        if not tf_files:
            print("No .tf files found to fix.")
            return []
        
        print(f"Found {len(tf_files)} Terraform files to fix...")
        
        for tf_file in tf_files:
            try:
                self.fix_file(tf_file)
            except Exception as e:
                print(f"Error fixing {tf_file}: {e}")
        
        return self.fixes_applied
    
    def fix_file(self, file_path: Path):
        """Fix syntax issues in a single Terraform file."""
        print(f"Fixing {file_path.name}...")
        
        # Read the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  Error reading {file_path}: {e}")
            return
        
        # Create backup
        backup_path = file_path.with_suffix('.tf.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        original_content = content
        
        # Apply fixes
        content = self._fix_resource_names(content)
        content = self._fix_missing_newlines(content)
        content = self._fix_invalid_characters(content)
        content = self._fix_missing_commas(content)
        content = self._remove_jinja_artifacts(content)
        content = self._fix_empty_assignments(content)
        content = self._fix_line_continuations(content)
        
        # Write the fixed content
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixes_applied.append(str(file_path))
            print(f"  Fixed {file_path.name}")
        else:
            print(f"  - No fixes needed for {file_path.name}")
            # Remove backup if no changes
            backup_path.unlink()
    
    def _fix_resource_names(self, content: str) -> str:
        """Fix invalid resource names."""
        # Fix resource names with spaces
        content = re.sub(
            r'resource\s+"([^"]+)"\s+"([^"]*)\s+([^"]*)"',
            lambda m: f'resource "{m.group(1)}" "{m.group(2).replace(" ", "_")}{m.group(3)}"',
            content
        )
        
        # Fix resource names starting with numbers
        content = re.sub(
            r'resource\s+"([^"]+)"\s+"(\d[^"]*)"',
            lambda m: f'resource "{m.group(1)}" "res_{m.group(2)}"',
            content
        )
        
        # Fix invalid characters in resource names
        def fix_resource_name(match):
            resource_type = match.group(1)
            resource_name = match.group(2)

            # Handle completely empty resource names
            if not resource_name or resource_name.strip() == "":
                fixed_name = "unnamed_resource"
            else:
                # Replace invalid characters with underscores
                fixed_name = re.sub(r'[^a-zA-Z0-9_]', '_', resource_name)

            # Ensure it doesn't start with a number
            if fixed_name and fixed_name[0].isdigit():
                fixed_name = f'res_{fixed_name}'

            return f'resource "{resource_type}" "{fixed_name}"'
        
        content = re.sub(r'resource\s+"([^"]+)"\s+"([^"]*)"', fix_resource_name, content)
        
        return content
    
    def _fix_missing_newlines(self, content: str) -> str:
        """Fix missing newlines after arguments."""
        # Fix multiple arguments on same line
        content = re.sub(
            r'"\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*=)',
            r'"\n  \1',
            content
        )
        
        # Fix missing newlines before blocks
        content = re.sub(
            r'"\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\{)',
            r'"\n  \1',
            content
        )

        # Fix missing newlines between closing braces and new blocks
        content = re.sub(
            r'\}\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\{)',
            r'}\n\1',
            content
        )
        
        # Fix missing newlines after closing brackets
        content = re.sub(
            r'\}\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*=)',
            r'}\n  \1',
            content
        )
        
        return content
    
    def _fix_invalid_characters(self, content: str) -> str:
        """Remove invalid characters and artifacts."""
        # Remove backticks and jinja artifacts
        content = re.sub(r'```jinja.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`+', '', content)
        
        return content
    
    def _fix_missing_commas(self, content: str) -> str:
        """Fix missing commas in JSON-like structures."""
        # Fix missing commas in tags and other maps
        content = re.sub(
            r'"\s*"([^"]+)"\s*=\s*"([^"]*)"',
            r'", "\1" = "\2"',
            content
        )
        
        # Fix specific patterns like tags
        content = re.sub(
            r'(\{"[^"]+"\s*=\s*"[^"]*")([^,}]+)(\})',
            r'\1, \2\3',
            content
        )
        
        return content
    
    def _remove_jinja_artifacts(self, content: str) -> str:
        """Remove leftover Jinja template artifacts."""
        # Remove comment lines with file paths
        content = re.sub(r'^//\s*File:.*$', '', content, flags=re.MULTILINE)

        # Remove extra newlines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content

    def _fix_empty_assignments(self, content: str) -> str:
        """Replace empty assignments with null to avoid invalid expressions."""
        content = re.sub(
            r'(=[ \t]*)(\n)',
            r'= null\2',
            content
        )
        return content
    
    def _fix_line_continuations(self, content: str) -> str:
        """Fix improper line continuations."""
        # Fix single-line blocks that should be multi-line
        content = re.sub(
            r'(\{)\s*([a-zA-Z_][a-zA-Z0-9_]*\s*=)',
            r'\1\n  \2',
            content
        )
        
        return content


def run_terraform_fmt(output_dir: Path) -> bool:
    """Run terraform fmt to format all files."""
    import subprocess
    import shutil
    
    # Check if terraform is installed
    if not shutil.which('terraform'):
        print("Warning: terraform command not found. Cannot run 'terraform fmt'.")
        print("Please install Terraform to auto-format the generated files.")
        return False
    
    try:
        result = subprocess.run(
            ['terraform', 'fmt'],
            cwd=output_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("Successfully ran 'terraform fmt'")
            return True
        else:
            print(f"Warning: 'terraform fmt' had issues: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Warning: 'terraform fmt' timed out")
        return False
    except Exception as e:
        print(f"Warning: Could not run 'terraform fmt': {e}")
        return False


def main():
    """Main function for command line usage."""
    if len(sys.argv) != 2:
        print("Usage: python template_fixer.py <output_directory>")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    if not output_dir.exists():
        print(f"Error: Directory {output_dir} does not exist")
        sys.exit(1)
    
    fixer = TerraformSyntaxFixer(output_dir)
    fixed_files = fixer.fix_all_files()
    
    if fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"  - {Path(file).name}")
        
        # Try to run terraform fmt
        print("\nRunning 'terraform fmt' to format files...")
        run_terraform_fmt(output_dir)
        
    else:
        print("\nNo files needed fixing.")
    
    print(f"\nBackup files created with .tf.backup extension")


if __name__ == "__main__":
    main()
