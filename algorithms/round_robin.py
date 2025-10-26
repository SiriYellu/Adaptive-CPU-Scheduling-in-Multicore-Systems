"""
Round Robin scheduling algorithm.
"""
from typing import List, Optional
from collections import deque
from algorithms.base_scheduler import BaseScheduler
from core.process import Process
from core.cpu import CPUCore


class RoundRobinScheduler(BaseScheduler):
    """
    Round Robin Scheduler.
    
    Each process gets a fixed time quantum in circular order.
    Preemptive algorithm with fair CPU sharing.
    
    Characteristics:
    - Fair allocation of CPU time
    - Good for time-sharing systems
    - Performance depends on time quantum size
    - No starvation
    """
    
    def __init__(self, num_cores: int, time_quantum: float = 4.0):
        super().__init__(num_cores, name=f"Round Robin (q={time_quantum})")
        self._time_quantum = time_quantum
        # Use a FIFO queue for round-robin behavior
        self.rr_queue = deque()
        self.process_quantum_remaining = {}
    
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select the next process from the round-robin queue.
        
        Args:
            core: CPU core requesting a process
            ready_queue: List of ready processes
            current_time: Current simulation time
            
        Returns:
            Next process in round-robin order or None if queue is empty
        """
        # Add new processes to the round-robin queue
        for process in ready_queue:
            if process not in self.rr_queue:
                self.rr_queue.append(process)
                self.process_quantum_remaining[process.pid] = self._time_quantum
        
        if not self.rr_queue:
            return None
        
        # Get the next process in round-robin order
        process = self.rr_queue[0]
        return process
    
    def on_process_completion(self, process: Process, current_time: float) -> None:
        """
        Remove completed process from round-robin queue.
        
        Args:
            process: The completed process
            current_time: Current simulation time
        """
        if process in self.rr_queue:
            self.rr_queue.remove(process)
        if process.pid in self.process_quantum_remaining:
            del self.process_quantum_remaining[process.pid]
    
    def rotate_queue(self, process: Process) -> None:
        """
        Move process to the end of the queue after its quantum expires.
        
        Args:
            process: Process to rotate
        """
        if process in self.rr_queue:
            self.rr_queue.remove(process)
            if not process.is_completed():
                self.rr_queue.append(process)
                # Reset quantum for this process
                self.process_quantum_remaining[process.pid] = self._time_quantum
    
    def is_preemptive(self) -> bool:
        """Round Robin is preemptive."""
        return True
    
    def get_time_quantum(self) -> float:
        """Return the configured time quantum."""
        return self._time_quantum
    
    def reset(self) -> None:
        """Reset scheduler state."""
        super().reset()
        self.rr_queue.clear()
        self.process_quantum_remaining.clear()

