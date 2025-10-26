"""
First-Come, First-Served (FCFS) scheduling algorithm.
"""
from typing import List, Optional
from algorithms.base_scheduler import BaseScheduler
from core.process import Process
from core.cpu import CPUCore


class FCFSScheduler(BaseScheduler):
    """
    First-Come, First-Served (FCFS) Scheduler.
    
    Processes are executed in the order they arrive.
    Non-preemptive algorithm.
    
    Characteristics:
    - Simple and fair
    - No starvation
    - Poor average waiting time (convoy effect)
    - Non-preemptive
    """
    
    def __init__(self, num_cores: int):
        super().__init__(num_cores, name="FCFS")
    
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select the process that arrived first (lowest arrival time).
        
        Args:
            core: CPU core requesting a process
            ready_queue: List of ready processes
            current_time: Current simulation time
            
        Returns:
            First process in queue or None if queue is empty
        """
        if not ready_queue:
            return None
        
        # Sort by arrival time and return the first one
        ready_queue.sort(key=lambda p: (p.arrival_time, p.pid))
        return ready_queue[0]
    
    def is_preemptive(self) -> bool:
        """FCFS is non-preemptive."""
        return False
    
    def get_time_quantum(self) -> float:
        """FCFS runs processes to completion."""
        return float('inf')

