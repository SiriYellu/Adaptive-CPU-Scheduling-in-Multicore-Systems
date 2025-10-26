"""
Work Stealing scheduling algorithm for multicore systems.
"""
from typing import List, Optional
import random
from algorithms.base_scheduler import BaseScheduler
from core.process import Process
from core.cpu import CPUCore


class WorkStealingScheduler(BaseScheduler):
    """
    Work Stealing Scheduler for multicore systems.
    
    Each core maintains its own local queue of processes.
    When a core becomes idle, it attempts to steal work from busy cores.
    
    Characteristics:
    - Excellent load balancing through dynamic work redistribution
    - Reduces idle time by allowing cores to steal work
    - Good for irregular workloads
    - Minimizes synchronization overhead
    - Based on the algorithm used in modern thread pools (e.g., Java Fork/Join)
    """
    
    def __init__(self, num_cores: int, steal_attempts: int = 3):
        super().__init__(num_cores, name="Work Stealing")
        self.steal_attempts = steal_attempts  # Number of cores to check when stealing
        
        # Each core has its own local queue
        self.core_queues = {i: [] for i in range(num_cores)}
        
        # Track process assignments
        self.process_core_map = {}
        
        # Global queue for initial process distribution
        self.global_queue = []
    
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select a process from the core's local queue, or steal from another core.
        
        Args:
            core: CPU core requesting a process
            ready_queue: List of ready processes (used for initial population)
            current_time: Current simulation time
            
        Returns:
            Selected process or None if no work available
        """
        core_id = core.core_id
        
        # First, populate local queues with new processes from ready_queue
        self._distribute_new_processes(ready_queue)
        
        # Try to get process from local queue
        if self.core_queues[core_id]:
            # Take from the front (FIFO within each core)
            process = self.core_queues[core_id].pop(0)
            return process
        
        # Local queue is empty, try to steal work
        stolen_process = self._steal_work(core_id, current_time)
        if stolen_process:
            return stolen_process
        
        return None
    
    def _distribute_new_processes(self, ready_queue: List[Process]) -> None:
        """
        Distribute new processes to core queues.
        Uses a simple round-robin distribution.
        
        Args:
            ready_queue: List of processes to distribute
        """
        new_processes = [p for p in ready_queue if p.pid not in self.process_core_map and p not in self.global_queue]
        
        for process in new_processes:
            self.global_queue.append(process)
        
        # Distribute processes from global queue to core queues
        while self.global_queue:
            # Find the core with the smallest queue
            min_queue_core = min(self.core_queues.keys(), key=lambda c: len(self.core_queues[c]))
            
            process = self.global_queue.pop(0)
            self.core_queues[min_queue_core].append(process)
            self.process_core_map[process.pid] = min_queue_core
    
    def _steal_work(self, thief_core_id: int, current_time: float) -> Optional[Process]:
        """
        Attempt to steal work from another core's queue.
        
        Args:
            thief_core_id: ID of the core attempting to steal
            current_time: Current simulation time
            
        Returns:
            Stolen process or None if no work to steal
        """
        # Get list of potential victim cores (exclude self)
        potential_victims = [i for i in range(self.num_cores) if i != thief_core_id]
        
        if not potential_victims:
            return None
        
        # Randomly sample cores to steal from (reduces contention)
        random.shuffle(potential_victims)
        cores_to_check = potential_victims[:self.steal_attempts]
        
        # Find the core with the most work
        best_victim = None
        max_queue_size = 0
        
        for victim_id in cores_to_check:
            queue_size = len(self.core_queues[victim_id])
            if queue_size > max_queue_size:
                max_queue_size = queue_size
                best_victim = victim_id
        
        # Only steal if victim has at least 2 processes (keep victim busy)
        if best_victim is not None and len(self.core_queues[best_victim]) >= 2:
            # Steal from the end of the queue (reduces contention with victim)
            stolen_process = self.core_queues[best_victim].pop()
            
            # Update tracking
            self.process_core_map[stolen_process.pid] = thief_core_id
            
            return stolen_process
        
        return None
    
    def add_process(self, process: Process) -> None:
        """
        Add a process to the global queue for distribution.
        
        Args:
            process: Process to add
        """
        if process.pid not in self.process_core_map:
            self.global_queue.append(process)
    
    def on_process_completion(self, process: Process, current_time: float) -> None:
        """
        Clean up tracking data for completed process.
        
        Args:
            process: Completed process
            current_time: Current simulation time
        """
        if process.pid in self.process_core_map:
            del self.process_core_map[process.pid]
        
        # Remove from any queue it might still be in
        for queue in self.core_queues.values():
            if process in queue:
                queue.remove(process)
    
    def get_queue_sizes(self) -> dict:
        """Get the size of each core's queue."""
        return {core_id: len(queue) for core_id, queue in self.core_queues.items()}
    
    def get_steal_statistics(self) -> dict:
        """Get statistics about work stealing operations."""
        return {
            'total_processes': len(self.process_core_map),
            'queue_sizes': self.get_queue_sizes(),
            'global_queue_size': len(self.global_queue)
        }
    
    def is_preemptive(self) -> bool:
        """Work stealing is generally non-preemptive within a core."""
        return False
    
    def get_time_quantum(self) -> float:
        """Use moderate time quantum to allow stealing opportunities."""
        return 10.0
    
    def reset(self) -> None:
        """Reset scheduler state."""
        super().reset()
        self.core_queues = {i: [] for i in range(self.num_cores)}
        self.process_core_map.clear()
        self.global_queue.clear()

