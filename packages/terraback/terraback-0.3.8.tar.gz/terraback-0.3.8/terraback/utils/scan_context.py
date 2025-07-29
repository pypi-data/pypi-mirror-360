"""Scan context for managing filters, dependencies and statistics."""
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
import threading

class ScanContext:
    """Thread-safe context for managing scan state and statistics."""
    
    def __init__(self):
        self._filters = defaultdict(dict)  # resource_type -> {filter_name: value}
        self._discovered_resources = defaultdict(list)  # resource_type -> [resource_ids]
        self._stats = {
            "resources_discovered": 0,
            "api_calls_made": 0,
            "api_calls_cached": 0,
            "api_calls_saved": 0,
            "total_api_calls": 0
        }
        self._lock = threading.Lock()
        self._dependency_graph = {}  # resource_type -> Set[dependencies]
    
    def add_filter(self, resource_type: str, filter_name: str, value: Any):
        """Add a filter for targeted scanning."""
        with self._lock:
            self._filters[resource_type][filter_name] = value
    
    def get_filters(self, resource_type: str) -> Dict[str, Any]:
        """Get filters for a resource type."""
        with self._lock:
            return self._filters.get(resource_type, {}).copy()
    
    def add_discovered_resource(self, resource_type: str, resource_id: str):
        """Track discovered resources for dependency resolution."""
        with self._lock:
            if resource_id not in self._discovered_resources[resource_type]:
                self._discovered_resources[resource_type].append(resource_id)
                self._stats["resources_discovered"] += 1
    
    def get_discovered_resources(self, resource_type: str) -> List[str]:
        """Get list of discovered resources of a type."""
        with self._lock:
            return self._discovered_resources.get(resource_type, []).copy()
    
    def update_stats(self, api_call: bool = False, cache_hit: bool = False, 
                    resources_found: int = 0):
        """Update scan statistics."""
        with self._lock:
            if api_call:
                self._stats["total_api_calls"] += 1
                if cache_hit:
                    self._stats["api_calls_cached"] += 1
                    self._stats["api_calls_saved"] += 1
                else:
                    self._stats["api_calls_made"] += 1
            
            if resources_found > 0:
                self._stats["resources_discovered"] += resources_found
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        with self._lock:
            stats = self._stats.copy()
            
            # Calculate cache hit rate
            if stats["total_api_calls"] > 0:
                hit_rate = stats["api_calls_cached"] / stats["total_api_calls"] * 100
                stats["cache_hit_rate"] = f"{hit_rate:.1f}%"
            else:
                stats["cache_hit_rate"] = "0.0%"
            
            return stats
    
    def optimize_scan_order(self, dependency_graph: Dict[str, Set[str]]) -> List[str]:
        """
        Optimize scan order based on dependencies using topological sort.
        Resources with no dependencies are scanned first.
        """
        # Create a copy of the graph
        graph = {k: set(v) for k, v in dependency_graph.items()}
        in_degree = defaultdict(int)
        
        # Calculate in-degrees
        for node, deps in graph.items():
            if node not in in_degree:
                in_degree[node] = 0
            for dep in deps:
                in_degree[dep] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node in graph if in_degree[node] == 0]
        result = []
        
        while queue:
            # Sort queue to ensure deterministic order
            queue.sort()
            node = queue.pop(0)
            result.append(node)
            
            # Remove edges from this node
            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Add any remaining nodes (in case of cycles)
        for node in graph:
            if node not in result:
                result.append(node)
        
        return result
    
    def should_scan_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Check if a resource should be scanned based on filters and discovered resources.
        """
        filters = self.get_filters(resource_type)
        
        # If there are specific resource_ids filter, check if this resource is included
        if 'resource_ids' in filters:
            return resource_id in filters['resource_ids']
        
        # Check if this resource was discovered as a dependency
        if resource_id in self.get_discovered_resources(resource_type):
            return True
        
        # If no filters, scan everything
        return not filters
    
    def clear(self):
        """Clear all context data."""
        with self._lock:
            self._filters.clear()
            self._discovered_resources.clear()
            self._stats = {
                "resources_discovered": 0,
                "api_calls_made": 0,
                "api_calls_cached": 0,
                "api_calls_saved": 0,
                "total_api_calls": 0
            }


# Global context instance
_context_instance = None

def get_scan_context() -> ScanContext:
    """Get or create the global scan context."""
    global _context_instance
    if _context_instance is None:
        _context_instance = ScanContext()
    return _context_instance

def reset_scan_context():
    """Reset the global scan context."""
    global _context_instance
    if _context_instance is not None:
        _context_instance.clear()
    _context_instance = None