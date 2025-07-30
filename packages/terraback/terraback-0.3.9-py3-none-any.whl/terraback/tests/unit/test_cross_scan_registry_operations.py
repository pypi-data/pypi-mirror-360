import json
from pathlib import Path

from terraback.utils.cross_scan_registry import CrossScanRegistry


def test_register_dependency(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache)
    reg.register_dependency("aws_vpc", "aws_subnet")
    assert reg.get_dependencies("aws_vpc") == ["aws_subnet"]
    assert cache.exists()


def test_cycle_detection(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache)
    reg.register_dependency("a", "b")
    reg.register_dependency("b", "c")
    reg.register_dependency("c", "a")  # would create cycle
    assert "a" not in reg.get_dependencies("c")


def test_save_and_load_registry(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache)
    reg.register("aws_vpc", "v1", {"name": "test"})
    reg.add_dependency("aws_vpc", "v1", "aws_subnet", "s1")

    reg2 = CrossScanRegistry(cache_file=cache)
    item = reg2.get_item("aws_vpc", "v1")
    assert item is not None
    assert item["data"]["name"] == "test"
    assert ("aws_subnet", "s1") in item["dependencies"]


def test_recursive_scan_traversal(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache)
    reg.register("aws_instance", "i1", {})
    reg.register("aws_subnet", "s1", {})
    reg.register("aws_vpc", "v1", {})
    reg.add_dependency("aws_instance", "i1", "aws_subnet", "s1")
    reg.add_dependency("aws_subnet", "s1", "aws_vpc", "v1")

    results = reg.recursive_scan("aws_instance", "i1")
    assert set(results) == {("aws_instance", "i1"), ("aws_subnet", "s1"), ("aws_vpc", "v1")}


def test_invalid_inputs(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache)

    reg.register_dependency(123, "valid")
    reg.register_dependency("valid", "")
    assert reg.registry == {}

    reg.register("type", "", {})
    reg.register("type", "id", "not-dict")
    assert reg.items == {}

    reg.add_dependency("aws_instance", "", "aws_subnet", "s1")
    reg.add_dependency("aws_instance", "i1", "aws_subnet", "")
    assert reg.get_item("aws_instance", "i1") is None


def test_auto_save_false_requires_flush(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache, auto_save=False)
    reg.register("aws_vpc", "v1", {})
    assert not cache.exists()

    reg.flush()
    assert cache.exists()


def test_autosave_mode_delays_save(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache)
    with reg.autosave_mode(False):
        reg.register("aws_vpc", "v1", {})
        assert reg._dirty
        assert not cache.exists()
    assert cache.exists()
    assert not reg._dirty


def test_autosave_mode_flushes_when_dirty(tmp_path: Path):
    cache = tmp_path / "registry.json"
    reg = CrossScanRegistry(cache_file=cache)
    with reg.autosave_mode(False):
        reg.register("aws_vpc", "v1", {"key": "val"})
        assert not cache.exists()
    assert cache.exists()
    with open(cache, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["items"]["aws_vpc"]["v1"]["data"]["key"] == "val"
