import json
import time
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Optional, Callable, Any
from functools import wraps
from contextlib import contextmanager
import typer
from terraback.utils.logging import get_logger

logger = get_logger(__name__)

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
            logger.info("[PERF] %s completed in %.2fs", func.__name__, duration)
            return result
        except (ValueError, TypeError, KeyError, AttributeError, IOError, NotImplementedError) as e:
            duration = time.time() - start_time
            logger.error("[PERF] %s failed after %.2fs: %s", func.__name__, duration, e)
            raise
        except (SystemExit, KeyboardInterrupt):
            raise
    return wrapper

class CrossScanRegistry:
    """Manage resource dependency graph and item metadata with caching."""

    def __init__(self, cache_file: Optional[Path] = None, auto_save: bool = True):
        self.cache_file = cache_file or Path("generated/.terraback/cross_scan_registry.json")
        self.auto_save = auto_save
        # Registry for type level dependencies
        self.registry: Dict[str, Set[str]] = defaultdict(set)
        # Storage for item level data and dependencies
        self.items: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        # Track if in-memory state has changes not persisted to disk
        self._dirty = False
        self._version = "2.0"
        self._load()

    def set_output_dir(self, output_dir: Path):
        new_cache_file = output_dir / ".terraback" / "cross_scan_registry.json"
        if new_cache_file != self.cache_file:
            self.cache_file = new_cache_file
            self._load()

    @contextmanager
    def autosave_mode(self, enabled: bool):
        """Temporarily switch the ``auto_save`` flag.

        Usage::

            with cross_scan_registry.autosave_mode(False):
                ...  # perform multiple registry operations

        Upon exiting the context the previous state is restored. If auto-save is
        re-enabled and there are unsaved changes, the registry will be saved
        automatically.
        """
        previous = self.auto_save
        self.auto_save = enabled
        try:
            yield
        finally:
            self.auto_save = previous
            if previous and not enabled and self._dirty:
                self._save()

    def _normalize(self, name: str) -> str:
        if not isinstance(name, str):
            raise TypeError("Resource type must be string")
        n = name.strip().lower().replace("-", "_").replace(" ", "_").replace(".", "_")
        if len(n) > 3 and n.endswith("s") and not n.endswith("ss"):
            # Avoid stripping the trailing 's' from words that naturally end
            # with 's' like those ending in 'us' or 'is' (e.g. "radius",
            # "analysis"). Only remove it for likely plurals such as
            # "instances" -> "instance".
            if not n.endswith("us") and not n.endswith("is"):
                n = n[:-1]
        if not n:
            raise ValueError("Resource type cannot be empty")
        return n

    def _generate_cache_hash(self) -> str:
        hash_payload = {
            "registry": {k: sorted(list(v)) for k, v in sorted(self.registry.items())},
            "items": {},
        }
        for r_type, items in sorted(self.items.items()):
            hash_payload["items"][r_type] = {}
            for item_id, meta in sorted(items.items()):
                deps = sorted([list(d) for d in meta.get("dependencies", set())])
                hash_payload["items"][r_type][item_id] = {
                    "data": meta.get("data", {}),
                    "dependencies": deps,
                }
        payload_str = json.dumps(hash_payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()[:16]

    def _load(self):
        if not self.cache_file.exists():
            self.registry = defaultdict(set)
            self.items = defaultdict(dict)
            self._dirty = False
            return
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            file_version = data.get('_metadata', {}).get('version', '1.0')
            if file_version != self._version:
                logger.warning(
                    "Cache version mismatch (%s vs %s). Rebuilding cache.",
                    file_version,
                    self._version,
                )
                self.registry = defaultdict(set)
                self.items = defaultdict(dict)
                self._dirty = True
                if self.auto_save:
                    self._save()
                else:
                    try:
                        self.cache_file.unlink()
                    except Exception as e:
                        logger.error(
                            "Could not delete mismatched cache file %s: %s",
                            self.cache_file,
                            e,
                        )
                return
            expected_hash = data.get('_metadata', {}).get('hash')
            registry_data = data.get('registry', {})
            items_data = data.get('items', {})

            self.registry.clear()
            self.items.clear()
            for k, v_list in registry_data.items():
                norm_key = self._normalize(k)
                valid_deps = {self._normalize(dep) for dep in v_list if isinstance(dep, str) and dep.strip()}
                self.registry[norm_key].update(valid_deps)

            for r_type, items in items_data.items():
                norm_type = self._normalize(r_type)
                if not isinstance(items, dict):
                    continue
                self.items[norm_type] = {}
                for item_id, meta in items.items():
                    if not isinstance(item_id, str):
                        continue
                    data_dict = meta.get("data", {}) if isinstance(meta, dict) else {}
                    deps_raw = meta.get("dependencies", []) if isinstance(meta, dict) else []
                    deps_set = set()
                    for dep in deps_raw:
                        if (
                            isinstance(dep, (list, tuple))
                            and len(dep) == 2
                            and isinstance(dep[0], str)
                            and isinstance(dep[1], str)
                        ):
                            deps_set.add((self._normalize(dep[0]), dep[1]))
                    self.items[norm_type][item_id] = {
                        "data": data_dict,
                        "dependencies": deps_set,
                    }

            if expected_hash and expected_hash != self._generate_cache_hash():
                logger.warning("Cache integrity check failed. Rebuilding dependencies.")
                self.registry = defaultdict(set)
                self.items = defaultdict(dict)
                self._dirty = False
        except Exception as e:
            logger.warning(
                "Could not load cross-scan registry from %s: %s. Starting fresh.",
                self.cache_file,
                e,
            )
            self.registry = defaultdict(set)
            self.items = defaultdict(dict)
            self._dirty = False
        else:
            self._dirty = False
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
                'items': {},
            }
            for r_type, items in self.items.items():
                cache_data['items'][r_type] = {}
                for item_id, meta in items.items():
                    deps = [list(d) for d in meta.get('dependencies', set())]
                    cache_data['items'][r_type][item_id] = {
                        'data': meta.get('data', {}),
                        'dependencies': deps,
                    }
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, "w", encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.cache_file)
            self._dirty = False
        except Exception as e:
            logger.error("Could not save cross-scan registry to %s: %s", self.cache_file, e)

    def flush(self):
        """Persist registry data to disk regardless of auto-save setting."""
        self._save()

    def register_dependency(self, source_resource_type: str, dependent_resource_type: str):
        try:
            source_key = self._normalize(source_resource_type)
            dep_key = self._normalize(dependent_resource_type)
        except Exception as e:
            logger.error("Invalid resource type in dependency registration: %s", e)
            return
        if source_key == dep_key:
            return
        if self._would_create_cycle(source_key, dep_key):
            logger.warning("Skipping dependency %s -> %s to avoid circular dependency", source_key, dep_key)
            return
        if dep_key not in self.registry[source_key]:
            self.registry[source_key].add(dep_key)
            self._dirty = True
            if self.auto_save:
                self._save()

    def register(self, resource_type: str, item_id: str, data: Dict[str, Any]):
        """Register an item and store its metadata."""
        try:
            norm_type = self._normalize(resource_type)
        except Exception as e:
            logger.error("Invalid resource type in register: %s", e)
            return
        if not isinstance(item_id, str) or not item_id:
            logger.error("item_id must be a non-empty string")
            return
        if not isinstance(data, dict):
            logger.error("data must be a dict")
            return
        entry = self.items.setdefault(norm_type, {}).setdefault(item_id, {"data": {}, "dependencies": set()})
        entry["data"] = data
        self._dirty = True
        if self.auto_save:
            self._save()

    def get_item(self, resource_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a previously stored item."""
        try:
            norm_type = self._normalize(resource_type)
        except Exception:
            return None
        item = self.items.get(norm_type, {}).get(item_id)
        if not item:
            return None
        # return a shallow copy to avoid external mutation
        result = {"data": item.get("data", {})}
        result["dependencies"] = list(item.get("dependencies", set()))
        return result

    def add_dependency(self, source_type: str, source_id: str, dep_type: str, dep_id: str):
        """Associate two items by dependency."""
        try:
            s_type = self._normalize(source_type)
            d_type = self._normalize(dep_type)
        except Exception as e:
            logger.error("Invalid resource type in add_dependency: %s", e)
            return
        if not all(isinstance(x, str) and x for x in (source_id, dep_id)):
            logger.error("item ids must be non-empty strings")
            return
        src_entry = self.items.setdefault(s_type, {}).setdefault(source_id, {"data": {}, "dependencies": set()})
        self.items.setdefault(d_type, {}).setdefault(dep_id, {"data": {}, "dependencies": set()})

        dep_pair = (d_type, dep_id)
        if dep_pair not in src_entry["dependencies"]:
            src_entry["dependencies"].add(dep_pair)
            # also track type level dependency for backward compatibility
            if d_type not in self.registry[s_type]:
                self.registry[s_type].add(d_type)
            self._dirty = True
            if self.auto_save:
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
            logger.error("Invalid resource type '%s': %s", resource_type, e)
            return []

    def recursive_scan(self, resource_type: str, item_id: str, visited: Optional[Set[tuple]] = None) -> List[tuple]:
        """Recursively traverse stored items and dependencies."""
        try:
            norm_type = self._normalize(resource_type)
        except Exception as e:
            logger.error("Invalid resource type '%s': %s", resource_type, e)
            return []

        if visited is None:
            visited = set()
        key = (norm_type, item_id)
        if key in visited:
            return []
        visited.add(key)

        results = [key]
        item = self.items.get(norm_type, {}).get(item_id)
        if not item:
            return results
        for dep_type, dep_id in item.get("dependencies", set()):
            results.extend(self.recursive_scan(dep_type, dep_id, visited))
        return results

    def clear(self):
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
            except Exception as e:
                logger.error("Could not delete cross-scan registry file %s: %s", self.cache_file, e)
        self.registry.clear()
        self.items.clear()
        self._dirty = True
        if self.auto_save:
            self._save()

# --- Singleton instance ---
cross_scan_registry = CrossScanRegistry()

def register_scan_function(resource_type: str, fn: Callable, tier: Any = None):
    """
    Register a scan function for a resource type, with optional license tier.
    """
    norm_type = cross_scan_registry._normalize(resource_type)
    if not callable(fn):
        logger.error("Scan function for '%s' must be callable", resource_type)
        return
    if norm_type in SCAN_FUNCTIONS:
        logger.warning("Overwriting scan function for resource type '%s'.", norm_type)
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
        logger.error("Invalid resource type '%s': %s", resource_type, e)
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
        logger.warning("[RECURSIVE_SCAN] No scan function registered for: %s", norm_type)
    else:
        scan_fn = scan_details["function"]
        sig = inspect.signature(scan_fn)
        filtered_kwargs = {key: value for key, value in kwargs_for_current_scan_fn.items() if key in sig.parameters}
        try:
            scan_fn(**filtered_kwargs)
        except Exception as e:
            logger.error("Error during scan of %s: %s", norm_type, e)

    dependencies = cross_scan_registry.get_dependencies(norm_type)
    for dep_type in dependencies:
        if dep_type not in visited:
            recursive_scan(
                dep_type,
                visited=visited,
                output_dir=output_dir,
                **kwargs_for_recursive_call
            )


@performance_monitor
def recursive_scan_all(
    visited: Optional[Set[str]] = None,
    output_dir: Path = Path("generated"),
    **caller_kwargs,
):
    """Recursively scan all registered resource types."""
    from terraback.core.license import check_feature_access, Tier
    if not check_feature_access(Tier.PROFESSIONAL):
        typer.secho(
            "Error: Recursive scanning requires a Professional license.",
            fg="red",
            bold=True,
        )
        raise typer.Exit(code=1)

    if visited is None:
        visited = set()

    for resource_type in list(SCAN_FUNCTIONS.keys()):
        recursive_scan(
            resource_type,
            visited=visited,
            output_dir=output_dir,
            **caller_kwargs,
        )
