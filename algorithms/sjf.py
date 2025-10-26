"""
Shortest Job First (SJF) scheduling algorithm.
"""
from typing import List, Optional
from algorithms.base_scheduler import BaseScheduler
from core.process import Process
from core.cpu import CPUCore


class SJFScheduler(BaseScheduler):
    """
    Shortest Job First (SJF) Scheduler.
    
    Selects the process with the shortest burst time.
    Can be non-preemptive or preemptive (SRTF - Shortest Remaining Time First).
    
    Characteristics:
    - Minimizes average waiting time
    - Can cause starvation of long processes
    - Requires knowledge of burst times
    """
    
    def __init__(self, num_cores: int, preemptive: bool = False):
        name = "SRTF" if preemptive else "SJF"
        super().__init__(num_cores, name=name)
        self._preemptive = preemptive
    
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select the process with the shortest remaining time.
        
        Args:
            core: CPU core requesting a process
            ready_queue: List of ready processes
            current_time: Current simulation time
            
        Returns:
            Process with shortest remaining time or None if queue is empty
        """
        if not ready_queue:
            return None
        
        # Sort by remaining time (shortest first), then by arrival time for ties
        ready_queue.sort(key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
        return ready_queue[0]
    
    def is_preemptive(self) -> bool:
        """Check if this is preemptive SJF (SRTF)."""
        return self._preemptive
    
    def should_preempt(self, current_process: Process, ready_queue: List[Process], current_time: float) -> bool:
        """
        In SRTF, preempt if a process with shorter remaining time arrives.
        
        Args:
            current_process: Currently running process
            ready_queue: Processes waiting to run
            current_time: Current simulation time
            
        Returns:
            True if should preempt
        """
        if not self._preemptive or not ready_queue:
            return False
        
        # Find the shortest job in ready queue
        shortest_job = min(ready_queue, key=lambda p: p.remaining_time)
        
        # Preempt if a shorter job is waiting
        return shortest_job.remaining_time < current_process.remaining_time
    
    def get_time_quantum(self) -> float:
        """
        For preemptive SJF (SRTF), use small time quantum.
        For non-preemptive SJF, run to completion.
        """
        return 1.0 if self._preemptive else float('inf')

