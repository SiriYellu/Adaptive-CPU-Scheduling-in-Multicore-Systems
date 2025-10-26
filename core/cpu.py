"""
CPU core simulation for multicore scheduling.
"""
from typing import Optional
from core.process import Process


class CPUCore:
    """
    Represents a single CPU core in a multicore system.
    
    Attributes:
        core_id: Unique identifier for this core
        current_process: Process currently executing on this core
        total_busy_time: Total time this core has been busy
        total_idle_time: Total time this core has been idle
        processes_executed: Number of processes executed on this core
        last_update_time: Last time the core state was updated
    """
    
    def __init__(self, core_id: int):
        self.core_id = core_id
        self.current_process: Optional[Process] = None
        self.total_busy_time = 0.0
        self.total_idle_time = 0.0
        self.processes_executed = 0
        self.last_update_time = 0.0
        self.is_busy = False
        
        # Load tracking
        self.load_history = []
        self.current_load = 0.0
    
    def assign_process(self, process: Process, current_time: float) -> None:
        """
        Assign a process to this CPU core.
        
        Args:
            process: Process to assign
            current_time: Current simulation time
        """
        if self.current_process is not None and not self.current_process.is_completed():
            # Update metrics for the previous process
            self._update_metrics(current_time)
        
        self.current_process = process
        self.is_busy = True
        self.last_update_time = current_time
        self.processes_executed += 1
    
    def execute_current_process(self, time_slice: float, current_time: float) -> Optional[float]:
        """
        Execute the current process for a given time slice.
        
        Args:
            time_slice: Maximum time to execute
            current_time: Current simulation time
            
        Returns:
            Actual time executed, or None if no process is running
        """
        if self.current_process is None:
            self._update_idle_time(current_time)
            return None
        
        actual_time = self.current_process.execute(time_slice, current_time, self.core_id)
        self.total_busy_time += actual_time
        self.last_update_time = current_time + actual_time
        
        # Update load
        self.current_load = self.current_process.remaining_time if not self.current_process.is_completed() else 0.0
        self.load_history.append(self.current_load)
        
        # If process completed, mark core as available
        if self.current_process.is_completed():
            self.current_process = None
            self.is_busy = False
        
        return actual_time
    
    def preempt_current_process(self, current_time: float) -> Optional[Process]:
        """
        Preempt the current process and return it.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            The preempted process, or None if no process is running
        """
        if self.current_process is None:
            return None
        
        self._update_metrics(current_time)
        process = self.current_process
        self.current_process = None
        self.is_busy = False
        self.current_load = 0.0
        
        return process
    
    def get_current_process(self) -> Optional[Process]:
        """Get the currently executing process."""
        return self.current_process
    
    def is_idle(self) -> bool:
        """Check if the core is idle."""
        return not self.is_busy or self.current_process is None
    
    def get_utilization(self, total_time: float) -> float:
        """
        Calculate CPU utilization percentage.
        
        Args:
            total_time: Total simulation time
            
        Returns:
            Utilization as a percentage (0.0 to 100.0)
        """
        if total_time == 0:
            return 0.0
        return (self.total_busy_time / total_time) * 100
    
    def get_load(self) -> float:
        """Get the current load on this core (remaining time of current process)."""
        return self.current_load
    
    def get_average_load(self) -> float:
        """Get the average load over time."""
        if not self.load_history:
            return 0.0
        return sum(self.load_history) / len(self.load_history)
    
    def _update_metrics(self, current_time: float) -> None:
        """Update internal metrics based on current time."""
        elapsed = current_time - self.last_update_time
        if self.is_busy:
            self.total_busy_time += elapsed
        else:
            self.total_idle_time += elapsed
        self.last_update_time = current_time
    
    def _update_idle_time(self, current_time: float) -> None:
        """Update idle time."""
        elapsed = current_time - self.last_update_time
        self.total_idle_time += elapsed
        self.last_update_time = current_time
    
    def reset(self) -> None:
        """Reset the core to initial state."""
        self.current_process = None
        self.total_busy_time = 0.0
        self.total_idle_time = 0.0
        self.processes_executed = 0
        self.last_update_time = 0.0
        self.is_busy = False
        self.current_load = 0.0
        self.load_history = []
    
    def __repr__(self) -> str:
        status = "BUSY" if self.is_busy else "IDLE"
        process_info = f", running P{self.current_process.pid}" if self.current_process else ""
        return f"Core-{self.core_id} [{status}]{process_info}"

