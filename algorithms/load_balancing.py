"""
Load Balancing scheduling algorithm for multicore systems.
"""
from typing import List, Optional
from algorithms.base_scheduler import BaseScheduler
from core.process import Process
from core.cpu import CPUCore


class LoadBalancingScheduler(BaseScheduler):
    """
    Load Balancing Scheduler for multicore systems.
    
    Distributes processes across cores to minimize load imbalance.
    Assigns new processes to the least loaded core.
    
    Characteristics:
    - Balances load across all cores
    - Considers current core load when assigning processes
    - Good for systems with variable process lengths
    - Minimizes waiting time by utilizing all cores efficiently
    """
    
    def __init__(self, num_cores: int, rebalance_threshold: float = 0.3):
        super().__init__(num_cores, name="Load Balancing")
        self.rebalance_threshold = rebalance_threshold  # Rebalance if load diff > 30%
        self.core_loads = {}  # Track load on each core
        self.process_assignments = {}  # Track which core each process is assigned to
    
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select a process for the requesting core, prioritizing processes
        assigned to this core or selecting from unassigned processes.
        
        Args:
            core: CPU core requesting a process
            ready_queue: List of ready processes
            current_time: Current simulation time
            
        Returns:
            Selected process or None if queue is empty
        """
        if not ready_queue:
            return None
        
        # First, check if any processes are assigned to this core
        assigned_processes = [p for p in ready_queue if self.process_assignments.get(p.pid) == core.core_id]
        
        if assigned_processes:
            # Return the process with shortest remaining time from assigned processes
            assigned_processes.sort(key=lambda p: (p.remaining_time, p.arrival_time))
            return assigned_processes[0]
        
        # If no assigned processes, select an unassigned process and assign it to this core
        unassigned_processes = [p for p in ready_queue if p.pid not in self.process_assignments]
        
        if unassigned_processes:
            # Assign the shortest job to this core
            unassigned_processes.sort(key=lambda p: (p.remaining_time, p.arrival_time))
            selected = unassigned_processes[0]
            self.process_assignments[selected.pid] = core.core_id
            self.core_loads[core.core_id] = self.core_loads.get(core.core_id, 0) + selected.remaining_time
            return selected
        
        # If all processes are assigned to other cores, check if we should rebalance
        return self._try_rebalance(core, ready_queue, current_time)
    
    def _try_rebalance(self, requesting_core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Attempt to rebalance by stealing work from heavily loaded cores.
        
        Args:
            requesting_core: Core requesting a process
            ready_queue: Available processes
            current_time: Current simulation time
            
        Returns:
            Process to steal or None
        """
        requesting_core_load = requesting_core.get_load()
        
        # Find processes assigned to heavily loaded cores
        candidates = []
        for process in ready_queue:
            assigned_core = self.process_assignments.get(process.pid)
            if assigned_core is None:
                continue
            
            assigned_core_load = self.core_loads.get(assigned_core, 0)
            
            # If the load difference is significant, consider stealing
            load_difference = assigned_core_load - requesting_core_load
            if load_difference > self.rebalance_threshold * assigned_core_load:
                candidates.append((process, load_difference))
        
        if candidates:
            # Steal the process that provides the best balance
            candidates.sort(key=lambda x: x[1], reverse=True)
            stolen_process = candidates[0][0]
            
            # Update assignments
            old_core = self.process_assignments[stolen_process.pid]
            self.process_assignments[stolen_process.pid] = requesting_core.core_id
            self.core_loads[old_core] = max(0, self.core_loads.get(old_core, 0) - stolen_process.remaining_time)
            self.core_loads[requesting_core.core_id] = self.core_loads.get(requesting_core.core_id, 0) + stolen_process.remaining_time
            
            return stolen_process
        
        return None
    
    def on_process_completion(self, process: Process, current_time: float) -> None:
        """
        Update load tracking when a process completes.
        
        Args:
            process: Completed process
            current_time: Current simulation time
        """
        if process.pid in self.process_assignments:
            assigned_core = self.process_assignments[process.pid]
            self.core_loads[assigned_core] = max(0, self.core_loads.get(assigned_core, 0) - process.burst_time)
            del self.process_assignments[process.pid]
    
    def get_core_loads(self) -> dict:
        """Get the current load on each core."""
        return self.core_loads.copy()
    
    def get_load_balance_score(self) -> float:
        """
        Calculate how well balanced the load is (0.0 to 1.0).
        1.0 = perfectly balanced, 0.0 = completely imbalanced.
        """
        if not self.core_loads:
            return 1.0
        
        loads = list(self.core_loads.values())
        if not loads:
            return 1.0
        
        avg_load = sum(loads) / len(loads)
        if avg_load == 0:
            return 1.0
        
        # Calculate coefficient of variation
        variance = sum((load - avg_load) ** 2 for load in loads) / len(loads)
        std_dev = variance ** 0.5
        cv = std_dev / avg_load if avg_load > 0 else 0
        
        # Convert to 0-1 scale (lower CV = better balance)
        return max(0.0, 1.0 - cv)
    
    def is_preemptive(self) -> bool:
        """Load balancing can be preemptive for rebalancing."""
        return True
    
    def get_time_quantum(self) -> float:
        """Use moderate time quantum for periodic rebalancing checks."""
        return 5.0
    
    def reset(self) -> None:
        """Reset scheduler state."""
        super().reset()
        self.core_loads.clear()
        self.process_assignments.clear()

