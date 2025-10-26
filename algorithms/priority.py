"""
Priority-based scheduling algorithm.
"""
from typing import List, Optional
from algorithms.base_scheduler import BaseScheduler
from core.process import Process, ProcessType
from core.cpu import CPUCore


class PriorityScheduler(BaseScheduler):
    """
    Priority-based Scheduler.
    
    Processes are scheduled based on their priority value.
    Lower priority number = higher priority.
    Can be preemptive or non-preemptive.
    
    Characteristics:
    - Important processes get CPU first
    - Risk of starvation for low-priority processes
    - Supports aging to prevent starvation
    """
    
    def __init__(self, num_cores: int, preemptive: bool = False, aging: bool = True):
        name = f"Priority ({'Preemptive' if preemptive else 'Non-preemptive'})"
        super().__init__(num_cores, name=name)
        self._preemptive = preemptive
        self._aging = aging
        self.aging_factor = 0.1  # Priority boost per time unit waiting
        self.process_wait_times = {}
    
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select the process with highest priority (lowest priority number).
        
        Args:
            core: CPU core requesting a process
            ready_queue: List of ready processes
            current_time: Current simulation time
            
        Returns:
            Highest priority process or None if queue is empty
        """
        if not ready_queue:
            return None
        
        # Apply aging if enabled
        if self._aging:
            self._apply_aging(ready_queue, current_time)
        
        # Sort by effective priority, then by arrival time for ties
        ready_queue.sort(key=lambda p: (self._get_effective_priority(p, current_time), p.arrival_time, p.pid))
        return ready_queue[0]
    
    def _get_effective_priority(self, process: Process, current_time: float) -> float:
        """
        Calculate effective priority with aging.
        
        Args:
            process: Process to calculate priority for
            current_time: Current simulation time
            
        Returns:
            Effective priority value
        """
        if not self._aging:
            return process.priority
        
        # Track wait time
        if process.pid not in self.process_wait_times:
            self.process_wait_times[process.pid] = process.arrival_time
        
        wait_time = current_time - self.process_wait_times[process.pid]
        
        # Apply aging: reduce priority number (increase actual priority) based on wait time
        effective_priority = process.priority - (wait_time * self.aging_factor)
        return max(0, effective_priority)  # Don't go below 0
    
    def _apply_aging(self, ready_queue: List[Process], current_time: float) -> None:
        """
        Apply aging to prevent starvation of low-priority processes.
        
        Args:
            ready_queue: List of processes to age
            current_time: Current simulation time
        """
        for process in ready_queue:
            if process.pid not in self.process_wait_times:
                self.process_wait_times[process.pid] = current_time
    
    def on_process_arrival(self, process: Process, current_time: float) -> None:
        """
        Track when process arrives for aging calculation.
        
        Args:
            process: Arriving process
            current_time: Current simulation time
        """
        self.process_wait_times[process.pid] = current_time
    
    def on_process_completion(self, process: Process, current_time: float) -> None:
        """
        Clean up tracking data for completed process.
        
        Args:
            process: Completed process
            current_time: Current simulation time
        """
        if process.pid in self.process_wait_times:
            del self.process_wait_times[process.pid]
    
    def is_preemptive(self) -> bool:
        """Check if this is preemptive priority scheduling."""
        return self._preemptive
    
    def should_preempt(self, current_process: Process, ready_queue: List[Process], current_time: float) -> bool:
        """
        Preempt if a higher priority process arrives.
        
        Args:
            current_process: Currently running process
            ready_queue: Processes waiting to run
            current_time: Current simulation time
            
        Returns:
            True if should preempt
        """
        if not self._preemptive or not ready_queue:
            return False
        
        current_priority = self._get_effective_priority(current_process, current_time)
        
        # Find highest priority process in ready queue
        highest_priority_process = min(ready_queue, key=lambda p: self._get_effective_priority(p, current_time))
        highest_priority = self._get_effective_priority(highest_priority_process, current_time)
        
        # Preempt if a higher priority process is waiting
        return highest_priority < current_priority
    
    def get_time_quantum(self) -> float:
        """
        For preemptive priority scheduling, use small time quantum to check for preemption.
        For non-preemptive, run to completion.
        """
        return 1.0 if self._preemptive else float('inf')
    
    def reset(self) -> None:
        """Reset scheduler state."""
        super().reset()
        self.process_wait_times.clear()

