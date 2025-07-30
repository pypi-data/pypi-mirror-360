import pytest
from terraback.utils.cross_scan_registry import CrossScanRegistry

def test_normalize_singular_suffixes():
    reg = CrossScanRegistry()
    assert reg._normalize("analysis") == "analysis"
    assert reg._normalize("radius") == "radius"


def test_normalize_plural_word():
    reg = CrossScanRegistry()
    assert reg._normalize("instances") == "instance"
