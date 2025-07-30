# terraback/utils/parallel_scan.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, List, Any, Callable, Optional
from pathlib import Path
import typer
import time


@dataclass
class ScanTask:
    """Represents a scan task for parallel execution."""
    name: str
    function: Callable
    kwargs: Dict[str, Any]
    
@dataclass
class ScanResult:
    """Result of a scan task execution."""
    name: str
    success: bool
    duration: float
    error: Optional[str] = None

class ParallelScanManager:
    """Manages parallel execution of scan tasks."""
    
    def __init__(self, max_workers: int = 8):
        """
        Initialize the parallel scan manager.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = min(max_workers, 32)  # Cap at 32 for stability
        
    def scan_parallel(self, tasks: List[ScanTask]) -> List[ScanResult]:
        """
        Execute scan tasks in parallel.
        
        Args:
            tasks: List of scan tasks to execute
            
        Returns:
            List of scan results
        """
        results = []
        total_tasks = len(tasks)
        completed = 0
        
        typer.echo(f"\nExecuting {total_tasks} scan tasks with {self.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_task, task): task
                for task in tasks
            }
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                result = future.result()
                results.append(result)
                
                completed += 1
                if result.success:
                    typer.echo(f"[{completed}/{total_tasks}] ✓ {result.name} ({result.duration:.1f}s)")
                else:
                    typer.echo(f"[{completed}/{total_tasks}] ✗ {result.name} - {result.error}")
                    
        return results
    
    def _execute_task(self, task: ScanTask) -> ScanResult:
        """
        Execute a single scan task.
        
        Args:
            task: The scan task to execute
            
        Returns:
            ScanResult with execution details
        """
        start_time = time.time()
        
        try:
            # Execute the scan function
            task.function(**task.kwargs)
            
            duration = time.time() - start_time
            return ScanResult(
                name=task.name,
                success=True,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return ScanResult(
                name=task.name,
                success=False,
                duration=duration,
                error=str(e)
            )

def create_scan_tasks(
    scan_configs: List[Dict[str, Any]], 
    base_kwargs: Dict[str, Any]
) -> List[ScanTask]:
    """
    Create scan tasks from configurations.
    
    Args:
        scan_configs: List of scan configurations with 'name' and 'function'
        base_kwargs: Base keyword arguments to pass to all scan functions
        
    Returns:
        List of ScanTask objects
    """
    tasks = []
    
    for config in scan_configs:
        task = ScanTask(
            name=config['name'],
            function=config['function'],
            kwargs=base_kwargs.copy()
        )
        tasks.append(task)
        
    return tasks
