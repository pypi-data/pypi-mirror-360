"""
Modular monitoring package for Sherlock AI

This package provides decorators and context managers for monitoring:
- Memory usage (Python heap, RSS, VMS)
- CPU utilization
- Disk I/O operations
- Network I/O operations
- Process resource consumption
"""

# Import all public classes and functions
from .decorators import monitor_memory, monitor_resources
from .context_managers import MemoryTracker, ResourceTracker
from .resource_monitor import ResourceMonitor
from .snapshots import ResourceSnapshot, MemorySnapshot
from .utils import log_memory_usage, log_resource_usage

# Export public API
__all__ = [
    # Decorators
    "monitor_memory",
    "monitor_resources",
    
    # Context managers
    "MemoryTracker",
    "ResourceTracker",
    
    # Utility classes
    "ResourceMonitor",
    
    # Data classes
    "ResourceSnapshot",
    "MemorySnapshot",
    
    # Utility functions
    "log_memory_usage",
    "log_resource_usage",
]