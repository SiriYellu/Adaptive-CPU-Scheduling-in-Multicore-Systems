"""
Adaptive scheduling algorithm that dynamically selects the best scheduler
based on system state and workload characteristics.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from algorithms.base_scheduler import BaseScheduler
from algorithms.fcfs import FCFSScheduler
from algorithms.sjf import SJFScheduler
from algorithms.round_robin import RoundRobinScheduler
from algorithms.priority import PriorityScheduler
from algorithms.load_balancing import LoadBalancingScheduler
from algorithms.work_stealing import WorkStealingScheduler
from core.process import Process, ProcessType
from core.cpu import CPUCore


class SystemState(Enum):
    """System load states."""
    LOW_LOAD = "low_load"
    MEDIUM_LOAD = "medium_load"
    HIGH_LOAD = "high_load"


class WorkloadCharacteristic(Enum):
    """Workload type characteristics."""
    CPU_INTENSIVE = "cpu_intensive"
    IO_INTENSIVE = "io_intensive"
    MIXED = "mixed"
    SHORT_JOBS = "short_jobs"
    LONG_JOBS = "long_jobs"


class AdaptiveScheduler(BaseScheduler):
    """
    Adaptive Scheduler that dynamically selects the best scheduling algorithm
    based on current system state and workload characteristics.
    
    The scheduler monitors:
    - System load (number of processes vs cores)
    - Process characteristics (CPU-bound vs I/O-bound)
    - Process burst times (short vs long jobs)
    - Core utilization
    - Historical performance
    
    And automatically switches between:
    - FCFS, SJF, Round Robin, Priority (traditional algorithms)
    - Load Balancing, Work Stealing (multicore algorithms)
    
    Decision Rules:
    1. High load + CPU-intensive → Load Balancing
    2. Low load + mixed workload → Work Stealing
    3. Short jobs + medium load → SJF
    4. Long jobs + high load → Round Robin
    5. Mixed workload + I/O intensive → Priority (with I/O priority)
    """
    
    def __init__(self, num_cores: int, adaptation_interval: float = 50.0):
        super().__init__(num_cores, name="Adaptive Scheduler")
        
        self.adaptation_interval = adaptation_interval
        self.last_adaptation_time = 0.0
        
        # Initialize all available schedulers
        self.schedulers = {
            'fcfs': FCFSScheduler(num_cores),
            'sjf': SJFScheduler(num_cores, preemptive=True),
            'round_robin': RoundRobinScheduler(num_cores, time_quantum=4.0),
            'priority': PriorityScheduler(num_cores, preemptive=True, aging=True),
            'load_balancing': LoadBalancingScheduler(num_cores),
            'work_stealing': WorkStealingScheduler(num_cores)
        }
        
        # Start with load balancing as default
        self.current_scheduler_name = 'load_balancing'
        self.current_scheduler = self.schedulers[self.current_scheduler_name]
        
        # Track system state
        self.system_state_history = []
        self.workload_history = []
        self.algorithm_usage = {name: 0 for name in self.schedulers.keys()}
        self.algorithm_performance = {name: [] for name in self.schedulers.keys()}
        
        # Performance tracking
        self.recent_processes = []
        self.recent_turnaround_times = []
        
    def select_process(self, core: CPUCore, ready_queue: List[Process], current_time: float) -> Optional[Process]:
        """
        Select a process using the currently active scheduler.
        Periodically adapts to change the active scheduler.
        
        Args:
            core: CPU core requesting a process
            ready_queue: List of ready processes
            current_time: Current simulation time
            
        Returns:
            Selected process or None
        """
        # Check if we should adapt the scheduling algorithm
        if current_time - self.last_adaptation_time >= self.adaptation_interval:
            self._adapt_scheduler(ready_queue, current_time)
            self.last_adaptation_time = current_time
        
        # Use current scheduler to select process
        return self.current_scheduler.select_process(core, ready_queue, current_time)
    
    def _adapt_scheduler(self, ready_queue: List[Process], current_time: float) -> None:
        """
        Analyze system state and switch to the most appropriate scheduler.
        
        Args:
            ready_queue: Current ready queue
            current_time: Current simulation time
        """
        # Analyze current system state
        system_state = self._analyze_system_state(ready_queue)
        workload_char = self._analyze_workload(ready_queue)
        
        # Store history
        self.system_state_history.append(system_state)
        self.workload_history.append(workload_char)
        
        # Select best algorithm based on state
        new_scheduler_name = self._select_best_algorithm(system_state, workload_char)
        
        if new_scheduler_name != self.current_scheduler_name:
            # Switch scheduler
            old_scheduler_name = self.current_scheduler_name
            self.current_scheduler_name = new_scheduler_name
            self.current_scheduler = self.schedulers[new_scheduler_name]
            
            # Transfer state from old scheduler to new one
            self._transfer_scheduler_state()
            
            print(f"[Adaptive] Switched from {old_scheduler_name} to {new_scheduler_name} at time {current_time:.1f}ms")
        
        # Track algorithm usage
        self.algorithm_usage[self.current_scheduler_name] += 1
    
    def _analyze_system_state(self, ready_queue: List[Process]) -> SystemState:
        """
        Analyze the current system load state.
        
        Args:
            ready_queue: Current ready queue
            
        Returns:
            SystemState enum value
        """
        queue_length = len(ready_queue)
        load_ratio = queue_length / self.num_cores
        
        if load_ratio < 1.0:
            return SystemState.LOW_LOAD
        elif load_ratio < 3.0:
            return SystemState.MEDIUM_LOAD
        else:
            return SystemState.HIGH_LOAD
    
    def _analyze_workload(self, ready_queue: List[Process]) -> WorkloadCharacteristic:
        """
        Analyze workload characteristics.
        
        Args:
            ready_queue: Current ready queue
            
        Returns:
            WorkloadCharacteristic enum value
        """
        if not ready_queue:
            return WorkloadCharacteristic.MIXED
        
        # Analyze process types
        cpu_intensive_count = sum(1 for p in ready_queue if p.process_type == ProcessType.CPU_BOUND)
        io_intensive_count = sum(1 for p in ready_queue if p.process_type == ProcessType.IO_BOUND)
        
        cpu_ratio = cpu_intensive_count / len(ready_queue)
        io_ratio = io_intensive_count / len(ready_queue)
        
        # Analyze burst times
        avg_burst = sum(p.remaining_time for p in ready_queue) / len(ready_queue)
        
        # Determine workload characteristic
        if cpu_ratio > 0.6:
            return WorkloadCharacteristic.CPU_INTENSIVE
        elif io_ratio > 0.6:
            return WorkloadCharacteristic.IO_INTENSIVE
        elif avg_burst < 10.0:
            return WorkloadCharacteristic.SHORT_JOBS
        elif avg_burst > 50.0:
            return WorkloadCharacteristic.LONG_JOBS
        else:
            return WorkloadCharacteristic.MIXED
    
    def _select_best_algorithm(self, system_state: SystemState, workload: WorkloadCharacteristic) -> str:
        """
        Select the best scheduling algorithm based on system state and workload.
        
        Args:
            system_state: Current system load state
            workload: Current workload characteristics
            
        Returns:
            Name of the best scheduler to use
        """
        # Decision matrix based on system state and workload
        
        # High load scenarios
        if system_state == SystemState.HIGH_LOAD:
            if workload == WorkloadCharacteristic.CPU_INTENSIVE:
                return 'load_balancing'  # Distribute CPU-intensive work evenly
            elif workload == WorkloadCharacteristic.LONG_JOBS:
                return 'round_robin'  # Ensure fairness for long jobs
            else:
                return 'load_balancing'  # Default for high load
        
        # Medium load scenarios
        elif system_state == SystemState.MEDIUM_LOAD:
            if workload == WorkloadCharacteristic.SHORT_JOBS:
                return 'sjf'  # Minimize waiting time for short jobs
            elif workload == WorkloadCharacteristic.IO_INTENSIVE:
                return 'priority'  # Prioritize I/O-bound processes
            else:
                return 'work_stealing'  # Good balance for mixed workload
        
        # Low load scenarios
        else:  # LOW_LOAD
            if workload == WorkloadCharacteristic.SHORT_JOBS:
                return 'sjf'  # Optimal for short jobs with low contention
            elif workload == WorkloadCharacteristic.MIXED:
                return 'work_stealing'  # Efficient for irregular workloads
            else:
                return 'fcfs'  # Simple and efficient for low load
    
    def _transfer_scheduler_state(self) -> None:
        """
        Transfer relevant state from the old scheduler to the new one.
        """
        # This is a simplified state transfer
        # In a more complex system, we might transfer queue contents, timing info, etc.
        pass
    
    def add_process(self, process: Process) -> None:
        """Add process to the current scheduler."""
        self.current_scheduler.add_process(process)
    
    def remove_process(self, process: Process) -> None:
        """Remove process from the current scheduler."""
        self.current_scheduler.remove_process(process)
    
    def on_process_arrival(self, process: Process, current_time: float) -> None:
        """Forward to current scheduler."""
        self.current_scheduler.on_process_arrival(process, current_time)
    
    def on_process_completion(self, process: Process, current_time: float) -> None:
        """
        Track process completion for performance analysis.
        
        Args:
            process: Completed process
            current_time: Current simulation time
        """
        self.recent_processes.append(process)
        self.recent_turnaround_times.append(process.turnaround_time)
        
        # Keep only recent history (last 20 processes)
        if len(self.recent_processes) > 20:
            self.recent_processes.pop(0)
            self.recent_turnaround_times.pop(0)
        
        # Track performance for current algorithm
        self.algorithm_performance[self.current_scheduler_name].append(process.turnaround_time)
        
        # Forward to current scheduler
        self.current_scheduler.on_process_completion(process, current_time)
    
    def is_preemptive(self) -> bool:
        """Delegate to current scheduler."""
        return self.current_scheduler.is_preemptive()
    
    def should_preempt(self, current_process: Process, ready_queue: List[Process], current_time: float) -> bool:
        """Delegate to current scheduler."""
        return self.current_scheduler.should_preempt(current_process, ready_queue, current_time)
    
    def get_time_quantum(self) -> float:
        """Delegate to current scheduler."""
        return self.current_scheduler.get_time_quantum()
    
    def get_current_algorithm(self) -> str:
        """Get the name of the currently active algorithm."""
        return self.current_scheduler_name
    
    def get_algorithm_usage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about algorithm usage.
        
        Returns:
            Dictionary with usage statistics
        """
        total_adaptations = sum(self.algorithm_usage.values())
        
        if total_adaptations == 0:
            return {name: 0.0 for name in self.algorithm_usage.keys()}
        
        return {
            name: (count / total_adaptations * 100)
            for name, count in self.algorithm_usage.items()
            if count > 0
        }
    
    def get_algorithm_performance_stats(self) -> Dict[str, float]:
        """
        Get average performance metrics for each algorithm.
        
        Returns:
            Dictionary mapping algorithm names to average turnaround times
        """
        stats = {}
        for name, turnaround_times in self.algorithm_performance.items():
            if turnaround_times:
                stats[name] = sum(turnaround_times) / len(turnaround_times)
            else:
                stats[name] = 0.0
        return stats
    
    def get_adaptation_history(self) -> List[tuple]:
        """
        Get the history of system states and algorithm selections.
        
        Returns:
            List of (system_state, workload_characteristic) tuples
        """
        return list(zip(self.system_state_history, self.workload_history))
    
    def reset(self) -> None:
        """Reset all schedulers and tracking data."""
        super().reset()
        for scheduler in self.schedulers.values():
            scheduler.reset()
        
        self.current_scheduler_name = 'load_balancing'
        self.current_scheduler = self.schedulers[self.current_scheduler_name]
        self.last_adaptation_time = 0.0
        
        self.system_state_history.clear()
        self.workload_history.clear()
        self.algorithm_usage = {name: 0 for name in self.schedulers.keys()}
        self.algorithm_performance = {name: [] for name in self.schedulers.keys()}
        self.recent_processes.clear()
        self.recent_turnaround_times.clear()
    
    def __repr__(self) -> str:
        return f"Adaptive Scheduler (Current: {self.current_scheduler_name}, Cores: {self.num_cores})"

