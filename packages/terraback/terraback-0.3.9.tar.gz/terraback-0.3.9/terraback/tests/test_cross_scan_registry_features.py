import json
import time
from pathlib import Path
from terraback.utils.cross_scan_registry import CrossScanRegistry


def test_set_output_dir_resets_on_version_mismatch(tmp_path: Path):
    new_dir = tmp_path / "new"
    cache_file = new_dir / ".terraback" / "cross_scan_registry.json"
    reg = CrossScanRegistry(cache_file=cache_file)
    reg.register("aws_vpc", "v1", {"name": "test"})
    reg.register_dependency("aws_vpc", "aws_subnet")
    assert reg.items
    assert reg.registry

    old_dir = tmp_path / "old"
    old_cache = old_dir / ".terraback" / "cross_scan_registry.json"
    old_cache.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "_metadata": {"version": "1.0", "hash": "", "timestamp": time.time()},
        "registry": {},
        "items": {},
    }
    old_cache.write_text(json.dumps(data))

    reg.set_output_dir(old_dir)
    assert reg.registry == {}
    assert reg.items == {}
    assert reg._dirty is False


def test_load_rewrites_old_version_file(tmp_path: Path):
    cache_file = tmp_path / "cross_scan_registry.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "_metadata": {"version": "1.0", "hash": "", "timestamp": time.time()},
        "registry": {"a": ["b"]},
        "items": {},
    }
    cache_file.write_text(json.dumps(data))

    reg = CrossScanRegistry(cache_file=cache_file)
    loaded = json.loads(cache_file.read_text())

    assert loaded["_metadata"]["version"] == reg._version
    assert reg.registry == {}
    assert reg.items == {}
    assert reg._dirty is False
