"""
Process class representing a process in the scheduling simulation.
"""
from enum import Enum
from typing import Optional


class ProcessState(Enum):
    """Enumeration of process states."""
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"


class ProcessType(Enum):
    """Type of process based on resource usage."""
    CPU_BOUND = "cpu_bound"
    IO_BOUND = "io_bound"
    MIXED = "mixed"


class Process:
    """
    Represents a process in the system.
    
    Attributes:
        pid: Process ID
        arrival_time: Time when process arrives in the system
        burst_time: Total CPU time required
        priority: Process priority (lower number = higher priority)
        remaining_time: Remaining burst time
        process_type: Type of process (CPU-bound, I/O-bound, or mixed)
        state: Current state of the process
        start_time: Time when process first starts execution
        completion_time: Time when process completes
        last_executed_time: Last time the process was executed
        waiting_time: Total time spent waiting
        turnaround_time: Total time from arrival to completion
        response_time: Time from arrival to first execution
        cpu_affinity: Preferred CPU core (optional)
    """
    
    def __init__(
        self,
        pid: int,
        arrival_time: float,
        burst_time: float,
        priority: int = 0,
        process_type: ProcessType = ProcessType.MIXED,
        cpu_affinity: Optional[int] = None
    ):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.process_type = process_type
        self.state = ProcessState.NEW
        self.cpu_affinity = cpu_affinity
        
        # Timing metrics
        self.start_time: Optional[float] = None
        self.completion_time: Optional[float] = None
        self.last_executed_time: Optional[float] = None
        self.waiting_time = 0.0
        self.turnaround_time = 0.0
        self.response_time = 0.0
        
        # Execution tracking
        self.executed_on_core: Optional[int] = None
        self.context_switches = 0
        self.time_quantum_used = 0.0
        
    def execute(self, time_slice: float, current_time: float, core_id: int) -> float:
        """
        Execute the process for a given time slice.
        
        Args:
            time_slice: Maximum time to execute
            current_time: Current simulation time
            core_id: ID of the CPU core executing this process
            
        Returns:
            Actual time executed
        """
        if self.state == ProcessState.NEW or self.state == ProcessState.READY:
            if self.start_time is None:
                self.start_time = current_time
                self.response_time = current_time - self.arrival_time
            self.state = ProcessState.RUNNING
        
        # Track context switches
        if self.executed_on_core is not None and self.executed_on_core != core_id:
            self.context_switches += 1
        self.executed_on_core = core_id
        
        # Calculate actual execution time
        actual_time = min(time_slice, self.remaining_time)
        self.remaining_time -= actual_time
        self.time_quantum_used += actual_time
        self.last_executed_time = current_time + actual_time
        
        # Update state
        if self.remaining_time <= 0:
            self.state = ProcessState.TERMINATED
            self.completion_time = current_time + actual_time
            self.turnaround_time = self.completion_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.burst_time
        else:
            self.state = ProcessState.READY
            
        return actual_time
    
    def is_completed(self) -> bool:
        """Check if the process has completed execution."""
        return self.state == ProcessState.TERMINATED
    
    def get_cpu_intensity(self) -> float:
        """
        Get the CPU intensity factor (0.0 to 1.0).
        Higher values mean more CPU-bound.
        """
        intensity_map = {
            ProcessType.CPU_BOUND: 0.9,
            ProcessType.MIXED: 0.5,
            ProcessType.IO_BOUND: 0.2
        }
        return intensity_map.get(self.process_type, 0.5)
    
    def __repr__(self) -> str:
        return (f"Process(pid={self.pid}, arrival={self.arrival_time:.1f}, "
                f"burst={self.burst_time:.1f}, remaining={self.remaining_time:.1f}, "
                f"priority={self.priority}, state={self.state.value})")
    
    def __lt__(self, other):
        """For priority queue comparisons (lower priority value = higher priority)."""
        return self.priority < other.priority

