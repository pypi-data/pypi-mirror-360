import json
import time
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Optional, Callable, Any
from functools import wraps
import typer

# Core scan function registry (metadata pattern)
SCAN_FUNCTIONS: Dict[str, Dict[str, Any]] = {}

def performance_monitor(func):
    """Monitor and log function execution time for performance tracking."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            typer.echo(f"[PERF] {func.__name__} completed in {duration:.2f}s", err=True)
            return result
        except (ValueError, TypeError, KeyError, AttributeError, IOError, NotImplementedError) as e:
            duration = time.time() - start_time
            typer.echo(f"[PERF] {func.__name__} failed after {duration:.2f}s: {e}", err=True)
            raise
        except (SystemExit, KeyboardInterrupt):
            raise
    return wrapper

class CrossScanRegistry:
    """
    Manages resource dependency graph with cache and cycle protection.
    """
    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or Path("generated/.terraback/cross_scan_registry.json")
        self.registry: Dict[str, Set[str]] = defaultdict(set)
        self._version = "2.0"
        self._load()

    def set_output_dir(self, output_dir: Path):
        new_cache_file = output_dir / ".terraback" / "cross_scan_registry.json"
        if new_cache_file != self.cache_file:
            self.cache_file = new_cache_file
            self._load()

    def _normalize(self, name: str) -> str:
        if not isinstance(name, str):
            raise TypeError("Resource type must be string")
        n = name.strip().lower().replace("-", "_").replace(" ", "_").replace(".", "_")
        if len(n) > 3 and n.endswith("s") and not n.endswith("ss"):
            n = n[:-1]
        if not n:
            raise ValueError("Resource type cannot be empty")
        return n

    def _generate_cache_hash(self) -> str:
        registry_str = json.dumps({k: sorted(list(v)) for k, v in sorted(self.registry.items())}, sort_keys=True)
        return hashlib.sha256(registry_str.encode()).hexdigest()[:16]

    def _load(self):
        if not self.cache_file.exists():
            self.registry = defaultdict(set)
            return
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            file_version = data.get('_metadata', {}).get('version', '1.0')
            if file_version != self._version:
                typer.echo(f"Warning: Cache version mismatch ({file_version} vs {self._version}). Rebuilding cache.", err=True)
                self.registry = defaultdict(set)
                return
            expected_hash = data.get('_metadata', {}).get('hash')
            registry_data = data.get('registry', {})
            self.registry.clear()
            for k, v_list in registry_data.items():
                norm_key = self._normalize(k)
                valid_deps = {self._normalize(dep) for dep in v_list if isinstance(dep, str) and dep.strip()}
                self.registry[norm_key].update(valid_deps)
            if expected_hash and expected_hash != self._generate_cache_hash():
                typer.echo("Warning: Cache integrity check failed. Rebuilding dependencies.", err=True)
                self.registry = defaultdict(set)
        except Exception as e:
            typer.echo(f"Warning: Could not load cross-scan registry from {self.cache_file}: {e}. Starting fresh.", err=True)
            self.registry = defaultdict(set)

    def _save(self):
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {
                '_metadata': {
                    'version': self._version,
                    'hash': self._generate_cache_hash(),
                    'timestamp': time.time(),
                },
                'registry': {k: sorted(list(v)) for k, v in self.registry.items()},
            }
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, "w", encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.cache_file)
        except Exception as e:
            typer.echo(f"Error: Could not save cross-scan registry to {self.cache_file}: {e}", err=True)

    def register_dependency(self, source_resource_type: str, dependent_resource_type: str):
        try:
            source_key = self._normalize(source_resource_type)
            dep_key = self._normalize(dependent_resource_type)
        except Exception as e:
            typer.echo(f"Error: Invalid resource type in dependency registration: {e}", err=True)
            return
        if source_key == dep_key:
            return
        if self._would_create_cycle(source_key, dep_key):
            typer.echo(f"Warning: Skipping dependency {source_key} -> {dep_key} to avoid circular dependency", err=True)
            return
        if dep_key not in self.registry[source_key]:
            self.registry[source_key].add(dep_key)
            self._save()

    def _would_create_cycle(self, source: str, target: str, visited: Optional[Set[str]] = None) -> bool:
        # Simple DFS for cycle detection
        if visited is None:
            visited = set()
        if target == source:
            return True
        if target in visited:
            return False
        visited.add(target)
        for dep in self.registry.get(target, set()):
            if self._would_create_cycle(source, dep, visited.copy()):
                return True
        return False

    def get_dependencies(self, resource_type: str) -> List[str]:
        try:
            norm_type = self._normalize(resource_type)
            return sorted(list(self.registry.get(norm_type, set())))
        except Exception as e:
            typer.echo(f"Error: Invalid resource type '{resource_type}': {e}", err=True)
            return []

    def clear(self):
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
            except Exception as e:
                typer.echo(f"Error: Could not delete cross-scan registry file {self.cache_file}: {e}", err=True)
        self.registry.clear()

# --- Singleton instance ---
cross_scan_registry = CrossScanRegistry()

def register_scan_function(resource_type: str, fn: Callable, tier: Any = None):
    """
    Register a scan function for a resource type, with optional license tier.
    """
    norm_type = cross_scan_registry._normalize(resource_type)
    if not callable(fn):
        typer.echo(f"Error: Scan function for '{resource_type}' must be callable", err=True)
        return
    if norm_type in SCAN_FUNCTIONS:
        typer.echo(f"Warning: Overwriting scan function for resource type '{norm_type}'.", err=True)
    SCAN_FUNCTIONS[norm_type] = {"function": fn, "tier": tier}

def get_all_scan_functions() -> Dict[str, Dict[str, Any]]:
    """
    Returns the complete dictionary of registered scan functions and their metadata.
    """
    return SCAN_FUNCTIONS

# --- Recursive scan (with performance monitoring) ---
import inspect
@performance_monitor
def recursive_scan(
    resource_type: str,
    visited: Optional[Set[str]] = None,
    output_dir: Path = Path("generated"),
    **caller_kwargs
):
    """
    Recursively scan a resource and its dependencies.
    """
    from terraback.core.license import check_feature_access, Tier
    # License check for recursive scanning
    if not check_feature_access(Tier.PROFESSIONAL):
        typer.secho("Error: Recursive scanning requires a Professional license.", fg="red", bold=True)
        raise typer.Exit(code=1)

    cross_scan_registry.set_output_dir(output_dir)
    try:
        norm_type = cross_scan_registry._normalize(resource_type)
    except Exception as e:
        typer.echo(f"Error: Invalid resource type '{resource_type}': {e}", err=True)
        return

    if visited is None:
        visited = set()
    if norm_type in visited:
        return
    visited.add(norm_type)

    # Prepare kwargs for recursive and scan function calls
    kwargs_for_recursive_call = dict(caller_kwargs)
    kwargs_for_recursive_call.pop('with_deps', None)
    kwargs_for_recursive_call.pop('output_dir', None)
    kwargs_for_current_scan_fn = dict(kwargs_for_recursive_call)
    kwargs_for_current_scan_fn['output_dir'] = output_dir

    scan_details = SCAN_FUNCTIONS.get(norm_type)
    if not scan_details or not callable(scan_details.get("function")):
        typer.echo(f"[RECURSIVE_SCAN] No scan function registered for: {norm_type}", err=True)
    else:
        scan_fn = scan_details["function"]
        sig = inspect.signature(scan_fn)
        filtered_kwargs = {key: value for key, value in kwargs_for_current_scan_fn.items() if key in sig.parameters}
        try:
            scan_fn(**filtered_kwargs)
        except Exception as e:
            typer.echo(f"Error during scan of {norm_type}: {e}", err=True)

    dependencies = cross_scan_registry.get_dependencies(norm_type)
    for dep_type in dependencies:
        if dep_type not in visited:
            recursive_scan(
                dep_type,
                visited=visited,
                output_dir=output_dir,
                **kwargs_for_recursive_call
            )
