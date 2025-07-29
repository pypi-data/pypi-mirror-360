import os
import re
from setuptools import setup, find_packages

# --- (The Final Fix: Robust Version Reading) ---
def get_version():
    """Reads the version from __version__.py without importing the package."""
    # The version file is at the root level, not inside terraback/
    version_file = "__version__.py"
    
    if not os.path.exists(version_file):
        # Fallback: try inside the package
        version_file = os.path.join("terraback", "__version__.py")
        if not os.path.exists(version_file):
            raise RuntimeError("Unable to find __version__.py file")
    
    with open(version_file) as f:
        version_content = f.read()
    
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")
# -----------------------------------------------

# Build universal package by default, unless specific tier requested
terraback_tier = os.environ.get("TERRABACK_TIER", "universal")

# Base dependencies for all tiers
install_requires=[
    # AWS SDK
    "boto3==1.38.21",
    "botocore==1.38.21",

    # Azure SDK
    "azure-identity==1.15.0",
    "azure-mgmt-resource==23.1.0",
    "azure-mgmt-compute==31.0.0",
    "azure-mgmt-network==27.0.0",
    "azure-mgmt-storage==21.2.0",
    "azure-mgmt-web==7.3.0",
    "azure-mgmt-sql==3.0.1",
    "azure-mgmt-keyvault==10.3.0",
    "azure-mgmt-monitor==6.0.0",
    "azure-core==1.30.0",

    # Google Cloud SDK
    "google-cloud-compute==1.14.0",
    "google-cloud-storage==2.10.0",
    "google-cloud-resource-manager==1.10.0",
    "google-auth==2.23.0",

    # CLI Framework & Display
    "typer[all]==0.15.4",
    "click==8.1.8",
    "rich==14.0.0",
    "colorama==0.4.6",
    "Pygments==2.19.1",

    # Templating
    "Jinja2==3.1.6",
    "MarkupSafe==3.0.2",

    # Utilities
    "requests",
    "cryptography",
    "paramiko",
    "pyyaml",
    "jmespath==1.0.1",
    "markdown-it-py==3.0.0",
    "mdurl==0.1.2",
    "python-dateutil==2.9.0.post0",
    "shellingham==1.5.4",
    "six==1.17.0",
    "typing_extensions>=4.0.0",
    "urllib3>=1.26.0,<2.0",
]

# Base entry points - always included
entry_points = {
    "console_scripts": [
        "terraback=terraback.cli.main:cli",
    ],
}

# Tier-specific adjustments
if terraback_tier == "universal":
    # Universal package includes all entry points
    entry_points["console_scripts"].extend([
        "terraback-migration=terraback.migration.cli:cli",
        "terraback-enterprise=terraback.enterprise.cli:cli",
    ])
    package_name = "terraback"
elif terraback_tier == "migration":
    entry_points["console_scripts"].append(
        "terraback-migration=terraback.migration.cli:cli"
    )
    package_name = f"terraback-{terraback_tier}"
elif terraback_tier == "enterprise":
    entry_points["console_scripts"].extend([
        "terraback-migration=terraback.migration.cli:cli",
        "terraback-enterprise=terraback.enterprise.cli:cli",
    ])
    package_name = f"terraback-{terraback_tier}"
else:  # community
    package_name = f"terraback-{terraback_tier}"

setup(
    name=package_name,
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'terraback': ['templates/**/*.j2'],
    },
    author="Terraback Team",
    author_email="support@terraback.io",
    description="Terraback: Universal infrastructure scanning and Terraform generation tool",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "Terraback: Infrastructure as Code generator",
    long_description_content_type="text/markdown",
    url="https://terraback.io",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Code Generators",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points=entry_points,
    install_requires=install_requires,
)