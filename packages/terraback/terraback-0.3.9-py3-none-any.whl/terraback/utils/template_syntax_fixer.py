#!/usr/bin/env python3
"""
Terraform Template Syntax Fixer for Terraback
Fixes common syntax issues in generated Terraform files
"""

import re
import sys
from terraback.utils.logging import get_logger
logger = get_logger(__name__)
from pathlib import Path
from typing import List, Tuple

# Precompiled regex patterns used throughout the fixer. Defining them at module
# level avoids recompiling the same expressions on each use.

# Leading comma patterns
LEADING_COMMA_RE = re.compile(r'^\s*,\s*(\"[^\"]+\"\s*=)')

# Malformed map patterns
MALFORMED_MAP_TRAILING_COMMA_RE = re.compile(r'(\w+\s*=\s*\{\s*),(\s*\})')
MALFORMED_MAP_EXTRA_COMMA_RE = re.compile(r'(\w+\s*=\s*\{\s*),\s*')

# Resource name patterns
RESOURCE_NAME_WITH_SPACES_RE = re.compile(r'resource\s+"([^"]+)"\s+"([^"]*)\s+([^"]*)"')
RESOURCE_NAME_STARTING_DIGIT_RE = re.compile(r'resource\s+"([^"]+)"\s+"(\d[^"]*)"')
RESOURCE_NAME_GENERIC_RE = re.compile(r'resource\s+"([^"]+)"\s+"([^"]*)"')
INVALID_RESOURCE_CHARS_RE = re.compile(r'[^a-zA-Z0-9_]')

# Missing newline patterns
MISSING_NEWLINE_ASSIGN_RE = re.compile(r'"\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*=)')
MISSING_NEWLINE_BLOCK_RE = re.compile(r'"\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\{)')
MISSING_NEWLINE_AFTER_BRACE_BLOCK_RE = re.compile(r'\}\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\{)')
MISSING_NEWLINE_AFTER_BRACE_ASSIGN_RE = re.compile(r'\}\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*=)')

# Invalid character patterns
REMOVE_JINJA_BLOCK_RE = re.compile(r'```jinja.*?```', flags=re.DOTALL)
REMOVE_CODE_BLOCK_RE = re.compile(r'```.*?```', flags=re.DOTALL)
REMOVE_BACKTICKS_RE = re.compile(r'`+')

# Missing comma patterns
MISSING_COMMA_RE = re.compile(r'(".*?"\s*=\s*".*?")\s+(".*?"\s*=)')

# Jinja artifact patterns
REMOVE_FILE_COMMENT_RE = re.compile(r'^//\s*File:.*$', flags=re.MULTILINE)
EXCESS_NEWLINES_RE = re.compile(r'\n\s*\n\s*\n')

# Empty assignment pattern
EMPTY_ASSIGN_RE = re.compile(r'(=[ \t]*)(\n)')

# Line continuation pattern
LINE_CONTINUATION_RE = re.compile(r'(\{)\s*([a-zA-Z_][a-zA-Z0-9_]*\s*=)')


class TerraformSyntaxFixer:
    """Fixes common Terraform syntax issues in generated files."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.fixes_applied = []

    def fix_all_files(self) -> List[str]:
        tf_files = list(self.output_dir.glob("*.tf"))
        if not tf_files:
            logger.info("No .tf files found to fix.")
            return []

        logger.info("Found %s Terraform files to fix...", len(tf_files))

        for tf_file in tf_files:
            try:
                self.fix_file(tf_file)
            except Exception as e:
                logger.error("Error fixing %s: %s", tf_file, e)

        return self.fixes_applied

    def fix_file(self, file_path: Path):
        logger.info("Fixing %s...", file_path.name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error("  Error reading %s: %s", file_path, e)
            return

        backup_path = file_path.with_suffix('.tf.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)

        original_content = content

        content = self._fix_leading_commas(content)
        content = self._fix_resource_names(content)
        content = self._fix_missing_newlines(content)
        content = self._fix_invalid_characters(content)
        content = self._fix_missing_commas(content)
        content = self._remove_jinja_artifacts(content)
        content = self._fix_empty_assignments(content)
        content = self._fix_line_continuations(content)
        content = self._fix_malformed_maps(content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixes_applied.append(str(file_path))
            logger.info("  Fixed %s", file_path.name)
        else:
            logger.info("  No fixes needed for %s", file_path.name)
            backup_path.unlink()

    def _fix_leading_commas(self, content: str) -> str:
        fixed_lines = []
        for line in content.splitlines():
            fixed_line = LEADING_COMMA_RE.sub(r'  \1', line)
            fixed_lines.append(fixed_line)
        return '\n'.join(fixed_lines)

    def _fix_malformed_maps(self, content: str) -> str:
        content = MALFORMED_MAP_TRAILING_COMMA_RE.sub(r'\1\2', content)
        content = MALFORMED_MAP_EXTRA_COMMA_RE.sub(r'\1', content)
        return content

    def _fix_resource_names(self, content: str) -> str:
        content = RESOURCE_NAME_WITH_SPACES_RE.sub(
            lambda m: f'resource "{m.group(1)}" "{m.group(2).replace(" ", "_")}{m.group(3)}"',
            content
        )
        content = RESOURCE_NAME_STARTING_DIGIT_RE.sub(
            lambda m: f'resource "{m.group(1)}" "res_{m.group(2)}"', content
        )

        def fix_resource_name(match):
            resource_type = match.group(1)
            resource_name = match.group(2)
            if not resource_name or resource_name.strip() == "":
                fixed_name = "unnamed_resource"
            else:
                fixed_name = INVALID_RESOURCE_CHARS_RE.sub('_', resource_name)
            if fixed_name and fixed_name[0].isdigit():
                fixed_name = f'res_{fixed_name}'
            return f'resource "{resource_type}" "{fixed_name}"'

        content = RESOURCE_NAME_GENERIC_RE.sub(fix_resource_name, content)
        return content

    def _fix_missing_newlines(self, content: str) -> str:
        content = MISSING_NEWLINE_ASSIGN_RE.sub(r'"\n  \1', content)
        content = MISSING_NEWLINE_BLOCK_RE.sub(r'"\n  \1', content)
        content = MISSING_NEWLINE_AFTER_BRACE_BLOCK_RE.sub(r'}\n\1', content)
        content = MISSING_NEWLINE_AFTER_BRACE_ASSIGN_RE.sub(r'}\n  \1', content)
        return content

    def _fix_invalid_characters(self, content: str) -> str:
        content = REMOVE_JINJA_BLOCK_RE.sub('', content)
        content = REMOVE_CODE_BLOCK_RE.sub('', content)
        content = REMOVE_BACKTICKS_RE.sub('', content)
        return content

    def _fix_missing_commas(self, content: str) -> str:
        content = MISSING_COMMA_RE.sub(r'\1, \2', content)
        return content

    def _remove_jinja_artifacts(self, content: str) -> str:
        content = REMOVE_FILE_COMMENT_RE.sub('', content)
        content = EXCESS_NEWLINES_RE.sub('\n\n', content)
        return content

    def _fix_empty_assignments(self, content: str) -> str:
        content = EMPTY_ASSIGN_RE.sub(r'= null\2', content)
        return content

    def _fix_line_continuations(self, content: str) -> str:
        content = LINE_CONTINUATION_RE.sub(r'\1\n  \2', content)
        return content


def run_terraform_fmt(output_dir: Path) -> bool:
    import subprocess
    import shutil

    if not shutil.which('terraform'):
        logger.warning("terraform command not found. Cannot run 'terraform fmt'.")
        logger.warning("Please install Terraform to auto-format the generated files.")
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
            logger.info("Successfully ran 'terraform fmt'")
            return True
        else:
            logger.warning("'terraform fmt' had issues: %s", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        logger.warning("'terraform fmt' timed out")
        return False
    except Exception as e:
        logger.warning("Could not run 'terraform fmt': %s", e)
        return False


def main():
    if len(sys.argv) != 2:
        logger.info("Usage: python template_syntax_fixer.py <output_directory>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    if not output_dir.exists():
        logger.error("Directory %s does not exist", output_dir)
        sys.exit(1)

    fixer = TerraformSyntaxFixer(output_dir)
    fixed_files = fixer.fix_all_files()

    if fixed_files:
        logger.info("\nFixed %s files:", len(fixed_files))
        for file in fixed_files:
            logger.info("  - %s", Path(file).name)

        logger.info("\nRunning 'terraform fmt' to format files...")
        if run_terraform_fmt(output_dir):
            logger.info("All files formatted successfully!")

    else:
        logger.info("\nNo files needed fixing.")

    logger.info("\nBackup files created with .tf.backup extension")


if __name__ == "__main__":
    main()
