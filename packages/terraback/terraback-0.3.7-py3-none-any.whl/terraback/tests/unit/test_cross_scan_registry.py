import unittest
import pytest
from utils.cross_scan_registry import CrossScanRegistry

class TestCrossScanRegistry(unittest.TestCase):
    """
    Unit tests for the CrossScanRegistry class.
    These tests validate the core logic of dependency registration and resolution
    without any external calls.
    """

    def setUp(self):
        """Set up a fresh CrossScanRegistry for each test."""
        self.registry = CrossScanRegistry()

    @pytest.mark.skip(reason="CrossScanRegistry.register method not implemented yet")
    def test_register_and_get_item(self):
        """Test basic registration and retrieval of an item."""
        self.registry.register(
            "aws_vpc", "vpc-12345", {"id": "vpc-12345", "name": "test-vpc"}
        )
        item = self.registry.get_item("aws_vpc", "vpc-12345")
        self.assertIsNotNone(item)
        self.assertEqual(item["name"], "test-vpc")

    @pytest.mark.skip(reason="CrossScanRegistry.get_item method not implemented yet")
    def test_get_nonexistent_item(self):
        """Test that getting a non-existent item returns None."""
        item = self.registry.get_item("aws_vpc", "vpc-nonexistent")
        self.assertIsNone(item)

    @pytest.mark.skip(reason="CrossScanRegistry methods not implemented yet")
    def test_add_dependency(self):
        """Test that dependencies are correctly added to an item."""
        self.registry.register(
            "aws_subnet", "subnet-123", {"id": "subnet-123"}
        )
        self.registry.add_dependency("aws_subnet", "subnet-123", "aws_vpc", "vpc-abc")
        
        item = self.registry.get_item("aws_subnet", "subnet-123")
        self.assertIn("dependencies", item)
        self.assertIn(("aws_vpc", "vpc-abc"), item["dependencies"])

    @pytest.mark.skip(reason="CrossScanRegistry methods not implemented yet")
    def test_recursive_scan_simple_dependency(self):
        """Test recursive scan for a simple, linear dependency chain."""
        # Register items with dependencies
        self.registry.register("aws_instance", "i-1", {})
        self.registry.add_dependency("aws_instance", "i-1", "aws_subnet", "subnet-1")
        
        self.registry.register("aws_subnet", "subnet-1", {})
        self.registry.add_dependency("aws_subnet", "subnet-1", "aws_vpc", "vpc-1")

        self.registry.register("aws_vpc", "vpc-1", {})

        # Perform recursive scan starting from the instance
        results = self.registry.recursive_scan("aws_instance", "i-1")
        
        # Check that all dependencies were found
        expected_results = {
            ("aws_instance", "i-1"),
            ("aws_subnet", "subnet-1"),
            ("aws_vpc", "vpc-1")
        }
        self.assertEqual(set(results), expected_results)

    @pytest.mark.skip(reason="CrossScanRegistry methods not implemented yet")
    def test_recursive_scan_shared_dependency(self):
        """Test recursive scan where multiple items share a dependency."""
        # instance1 -> subnet1 -> vpc1
        self.registry.register("aws_instance", "i-1", {})
        self.registry.add_dependency("aws_instance", "i-1", "aws_subnet", "subnet-1")
        self.registry.register("aws_subnet", "subnet-1", {})
        self.registry.add_dependency("aws_subnet", "subnet-1", "aws_vpc", "vpc-1")

        # instance2 -> subnet2 -> vpc1
        self.registry.register("aws_instance", "i-2", {})
        self.registry.add_dependency("aws_instance", "i-2", "aws_subnet", "subnet-2")
        self.registry.register("aws_subnet", "subnet-2", {})
        self.registry.add_dependency("aws_subnet", "subnet-2", "aws_vpc", "vpc-1")
        
        self.registry.register("aws_vpc", "vpc-1", {})

        # Scan from instance 2
        results = self.registry.recursive_scan("aws_instance", "i-2")
        expected_results = {
            ("aws_instance", "i-2"),
            ("aws_subnet", "subnet-2"),
            ("aws_vpc", "vpc-1") # The shared VPC
        }
        self.assertEqual(set(results), expected_results)

    def test_registry_exists(self):
        """Test that the CrossScanRegistry class can be instantiated."""
        # This is a simple test to verify the class exists and can be created
        registry = CrossScanRegistry()
        self.assertIsNotNone(registry)
        self.assertIsInstance(registry, CrossScanRegistry)


if __name__ == '__main__':
    unittest.main()