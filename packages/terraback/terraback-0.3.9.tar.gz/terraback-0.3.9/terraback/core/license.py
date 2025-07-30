# terraback/core/license.py
"""
License management with enhanced security for Terraback.

Security features:
- Machine fingerprinting (CPU, OS, hostname hash)
- Periodic online validation
- Offline grace period (30 days)
- Clock tampering detection
- Encrypted local validation cache
"""

import json
import os
import platform
import hashlib
import socket
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict
from enum import Enum
import requests
from functools import wraps
import typer
from cryptography.fernet import Fernet
import jwt
import subprocess
import base64

# Configuration
TERRABACK_LICENSE_DIR = Path.home() / ".terraback"
LICENSE_FILE = TERRABACK_LICENSE_DIR / "license.jwt"
METADATA_FILE = TERRABACK_LICENSE_DIR / "license_metadata.json"
VALIDATION_FILE = TERRABACK_LICENSE_DIR / "license_validation.enc"
TRIAL_FILE = TERRABACK_LICENSE_DIR / "trial.json"

# API endpoints
LICENSE_API_BASE = "https://jaejtnxq15.execute-api.us-east-1.amazonaws.com/prod"
TRIAL_API_BASE = "https://jaejtnxq15.execute-api.us-east-1.amazonaws.com/prod"

# Enhanced validation settings
class ValidationSettings:
    VALIDATION_INTERVAL_DAYS = 7  # How often to validate online
    OFFLINE_GRACE_DAYS = 30       # Allow offline use for 30 days
    MAX_OFFLINE_DAYS = 37         # Hard limit - 7 day buffer
    VALIDATION_ENDPOINT = f"{LICENSE_API_BASE}/v1/license/validate"
    ACTIVATION_ENDPOINT = f"{LICENSE_API_BASE}/v1/license/activate"
    TRIAL_ACTIVATION_ENDPOINT = f"{TRIAL_API_BASE}/v1/trial/activate"
    TRIAL_STATUS_ENDPOINT = f"{TRIAL_API_BASE}/v1/trial/status"

# Tier definitions
class Tier(Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

def _get_machine_fingerprint() -> str:
    """Generate a unique machine fingerprint combining multiple hardware/OS attributes."""
    components = []
    
    # CPU info
    try:
        cpu_info = platform.processor() or platform.machine()
        components.append(cpu_info)
    except:
        components.append("unknown-cpu")
    
    # OS info
    components.append(platform.system())
    components.append(platform.release())
    
    # Hostname (hashed for privacy)
    try:
        hostname = socket.gethostname()
        components.append(hashlib.md5(hostname.encode()).hexdigest()[:8])
    except:
        components.append("unknown-host")
    
    # MAC address of primary interface
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0,2*6,2)][::-1])
        components.append(mac)
    except:
        components.append("unknown-mac")
    
    # Create stable fingerprint
    fingerprint_string = '|'.join(components)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()

def _get_encryption_key() -> bytes:
    """Derive an encryption key from machine fingerprint."""
    fingerprint = _get_machine_fingerprint()
    # Use a fixed salt to ensure consistency
    salt = b"terraback-validation-2024"
    key_material = hashlib.pbkdf2_hmac('sha256', fingerprint.encode(), salt, 100000)
    return base64.urlsafe_b64encode(key_material[:32])

def _is_online() -> bool:
    """Check if we have internet connectivity."""
    try:
        response = requests.get(f"{LICENSE_API_BASE}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def _detect_clock_tampering(last_validation: Optional[datetime]) -> bool:
    """Detect if system clock has been tampered with."""
    if not last_validation:
        return False
    
    current_time = datetime.now(timezone.utc)
    
    # If current time is before last validation, clock was likely rolled back
    if current_time < last_validation:
        return True
    
    # If more than a year has passed instantly, clock was likely rolled forward
    time_diff = current_time - last_validation
    if time_diff.days > 365:
        return True
    
    return False

def _save_validation_data(validation_data: dict):
    """Save encrypted validation data."""
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        
        # Add timestamp
        validation_data['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Encrypt and save
        encrypted = fernet.encrypt(json.dumps(validation_data).encode())
        VALIDATION_FILE.write_bytes(encrypted)
    except Exception as e:
        # If encryption fails, delete the file to prevent bypass
        if VALIDATION_FILE.exists():
            VALIDATION_FILE.unlink()
        raise

def _load_validation_data() -> Optional[dict]:
    """Load and decrypt validation data."""
    if not VALIDATION_FILE.exists():
        return None
    
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        
        encrypted = VALIDATION_FILE.read_bytes()
        decrypted = fernet.decrypt(encrypted)
        data = json.loads(decrypted)
        
        # Parse timestamp
        if 'timestamp' in data:
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return data
    except:
        # If decryption fails, assume tampering
        if VALIDATION_FILE.exists():
            VALIDATION_FILE.unlink()
        return None

def _perform_online_validation(license_key: str) -> tuple[bool, Optional[dict]]:
    """Perform online license validation."""
    if not _is_online():
        return False, None
    
    try:
        machine_fingerprint = _get_machine_fingerprint()
        
        response = requests.post(
            ValidationSettings.VALIDATION_ENDPOINT,
            json={
                "license_key": license_key,
                "machine_fingerprint": machine_fingerprint,
                "validation_type": "periodic",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Save validation data
            validation_data = {
                "last_online_check": datetime.now(timezone.utc).isoformat(),
                "validation_count": result.get("validation_count", 0),
                "license_valid": True,
                "tier": result.get("tier", "community")
            }
            _save_validation_data(validation_data)
            
            return True, result
        else:
            # License is invalid or revoked
            if VALIDATION_FILE.exists():
                VALIDATION_FILE.unlink()
            return False, None
            
    except Exception:
        return False, None

def _should_validate_online() -> bool:
    """Check if online validation is needed."""
    validation_data = _load_validation_data()
    if not validation_data:
        return True
    
    last_check = validation_data.get('last_online_check')
    if not last_check:
        return True
    
    last_check_time = datetime.fromisoformat(last_check)
    current_time = datetime.now(timezone.utc)
    
    # Detect clock tampering
    if _detect_clock_tampering(last_check_time):
        return True
    
    days_since_check = (current_time - last_check_time).days
    
    return days_since_check >= ValidationSettings.VALIDATION_INTERVAL_DAYS

def get_license_path() -> Path:
    """Get the path to the license file."""
    return LICENSE_FILE

def get_metadata_path() -> Path:
    """Get the path to the metadata file."""
    return METADATA_FILE

def get_validation_path() -> Path:
    """Get the path to the validation file."""
    return VALIDATION_FILE

def get_active_license() -> Optional[Dict]:
    """
    Get the active license with enhanced validation.
    Returns None if no valid license exists or validation fails.
    """
    if not LICENSE_FILE.exists():
        return None
    
    try:
        # Read the stored JWT
        jwt_token = LICENSE_FILE.read_text().strip()
        
        # For public key verification, we'd need the public key
        # For now, decode without verification but check metadata
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        
        # Check if license has expired
        if 'exp' in decoded:
            exp_timestamp = decoded['exp']
            if datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
        
        # Load metadata for additional validation
        metadata = {}
        if METADATA_FILE.exists():
            metadata = json.loads(METADATA_FILE.read_text())
        
        # Check if online validation is needed
        if _should_validate_online():
            # Get license key from metadata
            license_key = metadata.get('license_key')
            if license_key:
                is_valid, _ = _perform_online_validation(license_key)
                if not is_valid:
                    # License failed online validation
                    return None
        else:
            # Check offline grace period
            validation_data = _load_validation_data()
            if validation_data:
                last_check = validation_data.get('last_online_check')
                if last_check:
                    last_check_time = datetime.fromisoformat(last_check)
                    current_time = datetime.now(timezone.utc)
                    days_offline = (current_time - last_check_time).days
                    
                    if days_offline > ValidationSettings.MAX_OFFLINE_DAYS:
                        # Exceeded offline grace period
                        return None
        
        # Format expiry for display
        expiry = 'Never'
        if 'exp' in decoded:
            exp_dt = datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)
            expiry = exp_dt.strftime('%Y-%m-%d')
        
        return {
            'email': decoded.get('email'),
            'tier': decoded.get('tier', 'community'),
            'expiry': expiry,
            'order_id': decoded.get('order_id'),
            'raw_jwt': jwt_token
        }
        
    except Exception:
        return None

def activate_license(key: str) -> bool:
    """
    Activate a license key with enhanced security.
    """
    # Ensure license directory exists
    TERRABACK_LICENSE_DIR.mkdir(exist_ok=True)
    
    try:
        # Normalize the key (remove spaces, dashes)
        normalized_key = key.strip().upper().replace('-', '').replace(' ', '')
        
        # Format to expected pattern if needed
        if len(normalized_key) == 16 and '-' not in key:
            formatted_key = '-'.join([normalized_key[i:i+4] for i in range(0, 16, 4)])
        else:
            formatted_key = key.strip()
        
        # Get machine fingerprint
        machine_fingerprint = _get_machine_fingerprint()
        
        # Try online activation first
        if _is_online():
            response = requests.post(
                ValidationSettings.ACTIVATION_ENDPOINT,
                json={
                    "license_key": formatted_key,
                    "machine_fingerprint": machine_fingerprint,
                    "validation_type": "activation",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                jwt_token = result.get('jwt_token')
                
                if jwt_token:
                    # Save the JWT
                    LICENSE_FILE.write_text(jwt_token)
                    
                    # Save metadata
                    metadata = {
                        'license_key': formatted_key,
                        'activation_time': datetime.now(timezone.utc).isoformat(),
                        'machine_fingerprint': machine_fingerprint,
                        'email': result.get('email'),
                        'tier': result.get('tier', 'community')
                    }
                    METADATA_FILE.write_text(json.dumps(metadata, indent=2))
                    
                    # Save initial validation data
                    validation_data = {
                        "last_online_check": datetime.now(timezone.utc).isoformat(),
                        "validation_count": 1,
                        "license_valid": True,
                        "tier": result.get('tier', 'community')
                    }
                    _save_validation_data(validation_data)
                    
                    return True
            else:
                # Handle specific error codes
                if response.status_code == 403:
                    typer.echo("Error: License is already activated on another machine", err=True)
                elif response.status_code == 404:
                    typer.echo("Error: Invalid license key", err=True)
                elif response.status_code == 410:
                    typer.echo("Error: License has expired", err=True)
                else:
                    typer.echo(f"Error: Activation failed ({response.status_code})", err=True)
                return False
        else:
            typer.echo("Error: Internet connection required for license activation", err=True)
            return False
            
    except Exception as e:
        typer.echo(f"Error activating license: {e}", err=True)
        return False

def get_active_tier() -> Tier:
    """
    Get the currently active feature tier based on license state.
    """
    if is_trial_active():
        return Tier.PROFESSIONAL
    
    license_data = get_active_license()
    if not license_data:
        return Tier.COMMUNITY
    
    tier_str = license_data.get('tier', 'community').lower()
    
    # Map tier strings to Tier enum
    tier_map = {
        'community': Tier.COMMUNITY,
        'professional': Tier.PROFESSIONAL,
        'enterprise': Tier.ENTERPRISE,
        # Handle potential variations
        'pro': Tier.PROFESSIONAL,
        'basic': Tier.COMMUNITY,
        'migration': Tier.PROFESSIONAL,  # Migration Pass = Professional
        'universal': Tier.COMMUNITY,  # Universal package build = Community tier by default
    }
    
    return tier_map.get(tier_str, Tier.COMMUNITY)

def check_feature_access(required_tier: Tier) -> bool:
    """Check if the current license tier has access to a feature."""
    current_tier = get_active_tier()
    
    # Define tier hierarchy
    tier_hierarchy = {
        Tier.COMMUNITY: 0,
        Tier.PROFESSIONAL: 1,
        Tier.ENTERPRISE: 2
    }
    
    return tier_hierarchy.get(current_tier, 0) >= tier_hierarchy.get(required_tier, 0)

def require_professional(func):
    """Decorator to require Professional tier for a command/function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not check_feature_access(Tier.PROFESSIONAL):
            typer.secho(
                "\n⚠️  This feature requires a Professional license.",
                fg=typer.colors.YELLOW,
                bold=True
            )
            typer.echo("Your current tier: Community")
            typer.echo("\nUpgrade options:")
            typer.echo("  • Get Migration Pass: https://terraback.io/pricing")
            typer.echo("  • Activate license: terraback license activate <key>")
            typer.echo("  • Start free trial: terraback trial start")
            raise typer.Exit(code=1)
        return func(*args, **kwargs)
    return wrapper

def require_enterprise(func):
    """Decorator to require Enterprise tier for a command/function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not check_feature_access(Tier.ENTERPRISE):
            typer.secho(
                "\n⚠️  This feature requires an Enterprise license.",
                fg=typer.colors.YELLOW,
                bold=True
            )
            current_tier = get_active_tier()
            typer.echo(f"Your current tier: {current_tier.value.capitalize()}")
            typer.echo("\nContact sales@terraback.io for Enterprise licensing")
            raise typer.Exit(code=1)
        return func(*args, **kwargs)
    return wrapper

def get_license_status() -> dict:
    """
    Get comprehensive license status information.
    """
    # Get active tier (handles trial, license, or community)
    active_tier = get_active_tier()
    
    # Base status
    status = {
        'active_tier': active_tier.value,  # This will now correctly show 'community' not 'universal'
        'has_license': False,
        'is_trial': is_trial_active()
    }
    
    # Add trial info if active
    if status['is_trial']:
        trial_info = get_trial_info()
        if trial_info:
            status.update({
                'has_license': True,  # Trial counts as having a license
                'tier': 'professional',  # Trials get professional features
                'expires': trial_info.get('end_date', 'Unknown'),
                'days_remaining': trial_info.get('days_remaining', 0)
            })
    
    # Check for actual license
    license_data = get_active_license()
    if license_data and not status['is_trial']:
        status.update({
            'has_license': True,
            'email': license_data.get('email'),
            'tier': license_data.get('tier', 'community').lower(),
            'expires': license_data.get('expiry', 'Unknown'),
            'order_id': license_data.get('order_id')
        })
        
        # Add validation info
        validation_info = get_validation_info()
        if 'days_since_online' in validation_info:
            status['days_since_online_validation'] = validation_info['days_since_online']
            status['validation_count'] = validation_info.get('validation_count', 0)
    
    return status

def get_validation_info() -> dict:
    """Get information about license validation status."""
    validation_data = _load_validation_data()
    if not validation_data:
        return {}
    
    last_check = validation_data.get('last_online_check')
    if not last_check:
        return {}
    
    last_check_time = datetime.fromisoformat(last_check)
    current_time = datetime.now(timezone.utc)
    days_since = (current_time - last_check_time).days
    
    info = {
        'days_since_online': days_since,
        'validation_count': validation_data.get('validation_count', 0),
        'needs_validation': days_since >= ValidationSettings.VALIDATION_INTERVAL_DAYS,
        'in_grace_period': ValidationSettings.OFFLINE_GRACE_DAYS <= days_since < ValidationSettings.MAX_OFFLINE_DAYS,
        'validation_expired': days_since >= ValidationSettings.MAX_OFFLINE_DAYS
    }
    
    if info['validation_expired']:
        info['validation_status'] = 'expired'
    elif info['in_grace_period']:
        info['validation_status'] = 'grace_period'
    else:
        info['validation_status'] = 'valid'
    
    return info

def force_license_refresh() -> bool:
    """Force an online license validation check."""
    license_data = get_active_license()
    if not license_data:
        return False
    
    # Get license key from metadata
    if METADATA_FILE.exists():
        metadata = json.loads(METADATA_FILE.read_text())
        license_key = metadata.get('license_key')
        
        if license_key:
            is_valid, _ = _perform_online_validation(license_key)
            return is_valid
    
    return False

# Trial functionality
def start_free_trial() -> bool:
    """
    Start a free 30-day Professional trial.
    Returns True if trial was successfully started.
    """
    # Check if trial already exists
    if is_trial_active():
        return False
    
    # Ensure directory exists
    TERRABACK_LICENSE_DIR.mkdir(exist_ok=True)
    
    try:
        machine_fingerprint = _get_machine_fingerprint()
        
        # Try online activation
        if _is_online():
            response = requests.post(
                ValidationSettings.TRIAL_ACTIVATION_ENDPOINT,
                json={
                    "machine_fingerprint": machine_fingerprint,
                    "platform": platform.system(),
                    "hostname": socket.gethostname()[:50],  # Truncate for privacy
                    "client_version": "0.0.1"  # You might want to import __version__
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Save trial data
                trial_data = {
                    "trial_id": result.get("trial_id"),
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "expires_at": result.get("expires_at"),
                    "machine_fingerprint": machine_fingerprint,
                    "days": 30
                }
                
                TRIAL_FILE.write_text(json.dumps(trial_data, indent=2))
                return True
            elif response.status_code == 409:
                error = response.json()
                if error.get("error") == "trial_already_used":
                    typer.echo("This machine has already used a free trial.", err=True)
                elif error.get("error") == "active_license_exists":
                    typer.echo("This machine already has an active license.", err=True)
                return False
        else:
            typer.echo("Internet connection required to start free trial.", err=True)
            return False
            
    except Exception as e:
        typer.echo(f"Error starting trial: {e}", err=True)
        return False

def is_trial_active() -> bool:
    """Check if a trial is currently active."""
    if not TRIAL_FILE.exists():
        return False
    
    try:
        trial_data = json.loads(TRIAL_FILE.read_text())
        expires_at = datetime.fromisoformat(trial_data["expires_at"].replace('Z', '+00:00'))
        
        if datetime.now(timezone.utc) < expires_at:
            # Verify machine fingerprint matches
            current_fingerprint = _get_machine_fingerprint()
            if trial_data.get("machine_fingerprint") == current_fingerprint:
                return True
        
        # Trial expired or fingerprint mismatch
        return False
        
    except Exception:
        return False

def get_trial_info() -> Optional[dict]:
    """Get trial information if active."""
    if not is_trial_active():
        return None
    
    try:
        trial_data = json.loads(TRIAL_FILE.read_text())
        expires_at = datetime.fromisoformat(trial_data["expires_at"].replace('Z', '+00:00'))
        started_at = datetime.fromisoformat(trial_data["started_at"].replace('Z', '+00:00'))
        
        now = datetime.now(timezone.utc)
        days_remaining = max(0, (expires_at - now).days)
        days_used = (now - started_at).days
        
        return {
            "trial_id": trial_data.get("trial_id"),
            "started_at": started_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "days_remaining": days_remaining,
            "days_used": days_used,
            "total_days": trial_data.get("days", 30),
            "start_date": started_at.strftime('%Y-%m-%d'),
            "end_date": expires_at.strftime('%Y-%m-%d')
        }
        
    except Exception:
        return None
