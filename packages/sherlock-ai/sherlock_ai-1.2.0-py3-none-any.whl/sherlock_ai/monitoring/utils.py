"""
Utility functions for monitoring
"""

import logging
from typing import Optional

from .snapshots import ResourceSnapshot, MemorySnapshot
from .resource_monitor import ResourceMonitor

logger = logging.getLogger("MonitoringLogger")

# Helper functions for logging
def log_memory_usage(function_name: str, start_memory: MemorySnapshot, end_memory: MemorySnapshot,
                     execution_time: float, success: bool, log_level: str, error: str = None):
    """Log memory usage information"""
    status = "SUCCESS" if success else "ERROR"
    
    # Calculate memory changes
    memory_change = end_memory.current_size - start_memory.current_size
    memory_change_str = ResourceMonitor.format_bytes(abs(memory_change))
    memory_change_sign = "+" if memory_change >= 0 else "-"
    
    current_memory_str = ResourceMonitor.format_bytes(end_memory.current_size)
    
    # Build log message
    log_msg = f"MEMORY | {function_name} | {status} | {execution_time:.3f}s | Current: {current_memory_str} | Change: {memory_change_sign}{memory_change_str}"
    
    # Add tracemalloc info if available
    if end_memory.traced_memory[0] > 0:
        traced_current = ResourceMonitor.format_bytes(end_memory.traced_memory[0])
        traced_peak = ResourceMonitor.format_bytes(end_memory.traced_memory[1])
        log_msg += f" | Traced: {traced_current} (Peak: {traced_peak})"
    
    if error:
        log_msg += f" | Error: {error}"
    
    log_method = getattr(logger, log_level.lower())
    log_method(log_msg)


def log_resource_usage(function_name: str, start_resources: Optional[ResourceSnapshot], 
                       end_resources: Optional[ResourceSnapshot], execution_time: float,
                       success: bool, log_level: str, include_io: bool, include_network: bool, error: str = None):
    """Log comprehensive resource usage information"""
    status = "SUCCESS" if success else "ERROR"
    
    if start_resources is None or end_resources is None:
        log_msg = f"RESOURCES | {function_name} | {status} | {execution_time:.3f}s | Resource monitoring unavailable"
    else:
        diff = ResourceMonitor.calculate_resource_diff(start_resources, end_resources)
        
        # Build basic log message
        current_memory = ResourceMonitor.format_bytes(end_resources.memory_rss)
        memory_change = ResourceMonitor.format_bytes(abs(diff["memory_rss_change"]))
        memory_sign = "+" if diff["memory_rss_change"] >= 0 else "-"
        
        log_msg = (f"RESOURCES | {function_name} | {status} | {execution_time:.3f}s | "
                  f"CPU: {end_resources.cpu_percent:.1f}% | "
                  f"Memory: {current_memory} ({memory_sign}{memory_change}) | "
                  f"Threads: {end_resources.num_threads}")
        
        # Add I/O information if requested
        if include_io and (diff["io_read_bytes"] > 0 or diff["io_write_bytes"] > 0):
            io_read = ResourceMonitor.format_bytes(diff["io_read_bytes"])
            io_write = ResourceMonitor.format_bytes(diff["io_write_bytes"])
            log_msg += f" | I/O: R:{io_read} W:{io_write}"
        
        # Add network information if requested
        if include_network and (diff["net_bytes_sent"] > 0 or diff["net_bytes_recv"] > 0):
            net_sent = ResourceMonitor.format_bytes(diff["net_bytes_sent"])
            net_recv = ResourceMonitor.format_bytes(diff["net_bytes_recv"])
            log_msg += f" | Net: S:{net_sent} R:{net_recv}"
    
    if error:
        log_msg += f" | Error: {error}"
    
    log_method = getattr(logger, log_level.lower())
    log_method(log_msg)