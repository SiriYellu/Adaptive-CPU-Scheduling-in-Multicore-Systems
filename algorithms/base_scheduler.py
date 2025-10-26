"""
Base scheduler class that all scheduling algorithms inherit from.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from core.process import Process
from core.cpu import CPUCore


class BaseScheduler(ABC):
    """
    Abstract base class for all scheduling algorithms.
    
    All schedulers must implement the select_process method and can optionally
    override other methods for specific behavior.
    """
    
    def __init__(self, num_cores: int, name: str = "Base Scheduler"):
        self.num_cores = num_cores
        self.name = name
        self.ready_queue: List[Process] = []
        self.total_context_switches = 0
        
    @abstractmethod
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select the next process to run on the given core.
        
        Args:
            core: The CPU core that needs a process
            ready_queue: List of processes in ready state
            current_time: Current simulation time
            
        Returns:
            Selected process or None if no suitable process is available
        """
        pass
    
    def add_process(self, process: Process) -> None:
        """
        Add a process to the ready queue.
        
        Args:
            process: Process to add to ready queue
        """
        self.ready_queue.append(process)
    
    def remove_process(self, process: Process) -> None:
        """
        Remove a process from the ready queue.
        
        Args:
            process: Process to remove
        """
        if process in self.ready_queue:
            self.ready_queue.remove(process)
    
    def get_time_quantum(self) -> float:
        """
        Get the time quantum for this scheduler.
        Default is infinity (non-preemptive).
        
        Returns:
            Time quantum in milliseconds
        """
        return float('inf')
    
    def is_preemptive(self) -> bool:
        """
        Check if this scheduler is preemptive.
        
        Returns:
            True if preemptive, False otherwise
        """
        return False
    
    def should_preempt(self, current_process: Process, ready_queue: List[Process], current_time: float) -> bool:
        """
        Determine if the current process should be preempted.
        
        Args:
            current_process: Currently running process
            ready_queue: Processes waiting to run
            current_time: Current simulation time
            
        Returns:
            True if current process should be preempted
        """
        return False
    
    def on_process_arrival(self, process: Process, current_time: float) -> None:
        """
        Called when a new process arrives in the system.
        Can be overridden for algorithm-specific behavior.
        
        Args:
            process: The arriving process
            current_time: Current simulation time
        """
        pass
    
    def on_process_completion(self, process: Process, current_time: float) -> None:
        """
        Called when a process completes execution.
        Can be overridden for algorithm-specific behavior.
        
        Args:
            process: The completed process
            current_time: Current simulation time
        """
        pass
    
    def reset(self) -> None:
        """Reset scheduler state."""
        self.ready_queue.clear()
        self.total_context_switches = 0
    
    def get_name(self) -> str:
        """Get the name of the scheduling algorithm."""
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.name} (Cores: {self.num_cores}, Queue: {len(self.ready_queue)})"

