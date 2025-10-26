"""
Main multicore CPU scheduler simulator.
"""
import random
from typing import List, Optional, Dict, Any
from core.process import Process, ProcessType, ProcessState
from core.cpu import CPUCore
from core.metrics import MetricsCollector, PerformanceMetrics
from algorithms.base_scheduler import BaseScheduler


class MulticoreSchedulerSimulator:
    """
    Multicore CPU Scheduler Simulator.
    
    Simulates a multicore system with configurable number of cores
    and various scheduling algorithms.
    """
    
    def __init__(self, num_cores: int = 4, verbose: bool = True):
        """
        Initialize the simulator.
        
        Args:
            num_cores: Number of CPU cores
            verbose: Whether to print simulation progress
        """
        self.num_cores = num_cores
        self.verbose = verbose
        
        # Create CPU cores
        self.cores: List[CPUCore] = [CPUCore(i) for i in range(num_cores)]
        
        # Process management
        self.all_processes: List[Process] = []
        self.ready_queue: List[Process] = []
        self.completed_processes: List[Process] = []
        
        # Scheduler
        self.scheduler: Optional[BaseScheduler] = None
        
        # Simulation state
        self.current_time = 0.0
        self.total_context_switches = 0
        
        # Results
        self.metrics: Optional[PerformanceMetrics] = None
    
    def set_scheduler(self, scheduler: BaseScheduler) -> None:
        """
        Set the scheduling algorithm to use.
        
        Args:
            scheduler: Scheduler instance
        """
        self.scheduler = scheduler
        if self.verbose:
            print(f"Scheduler set to: {scheduler.get_name()}")
    
    def generate_processes(
        self,
        num_processes: int,
        arrival_rate: float = 5.0,
        min_burst: float = 5.0,
        max_burst: float = 50.0,
        workload_type: str = 'mixed',
        priority_range: tuple = (0, 10)
    ) -> None:
        """
        Generate random processes for simulation.
        
        Args:
            num_processes: Number of processes to generate
            arrival_rate: Average time between process arrivals
            min_burst: Minimum burst time
            max_burst: Maximum burst time
            workload_type: Type of workload ('cpu_bound', 'io_bound', or 'mixed')
            priority_range: Tuple of (min_priority, max_priority)
        """
        self.all_processes.clear()
        current_arrival_time = 0.0
        
        for i in range(num_processes):
            # Generate arrival time (exponential distribution for realistic arrivals)
            if i > 0:
                inter_arrival = random.expovariate(1.0 / arrival_rate)
                current_arrival_time += inter_arrival
            
            # Generate burst time
            burst_time = random.uniform(min_burst, max_burst)
            
            # Determine process type based on workload
            if workload_type == 'cpu_bound':
                process_type = ProcessType.CPU_BOUND
            elif workload_type == 'io_bound':
                process_type = ProcessType.IO_BOUND
            else:  # mixed
                process_type = random.choice([ProcessType.CPU_BOUND, ProcessType.IO_BOUND, ProcessType.MIXED])
            
            # Generate priority
            priority = random.randint(priority_range[0], priority_range[1])
            
            # Create process
            process = Process(
                pid=i,
                arrival_time=current_arrival_time,
                burst_time=burst_time,
                priority=priority,
                process_type=process_type
            )
            
            self.all_processes.append(process)
        
        if self.verbose:
            print(f"Generated {num_processes} processes (workload: {workload_type})")
            print(f"  Arrival times: 0.0 to {current_arrival_time:.2f}ms")
            print(f"  Burst times: {min_burst:.1f} to {max_burst:.1f}ms")
    
    def add_process(self, process: Process) -> None:
        """
        Add a process to the simulation.
        
        Args:
            process: Process to add
        """
        self.all_processes.append(process)
    
    def run_simulation(self, max_time: Optional[float] = None) -> PerformanceMetrics:
        """
        Run the scheduling simulation.
        
        Args:
            max_time: Maximum simulation time (None for unlimited)
            
        Returns:
            PerformanceMetrics with simulation results
        """
        if self.scheduler is None:
            raise ValueError("No scheduler set. Use set_scheduler() first.")
        
        if not self.all_processes:
            raise ValueError("No processes to simulate. Use generate_processes() or add_process() first.")
        
        # Reset simulation state
        self._reset_simulation()
        
        # Sort processes by arrival time
        self.all_processes.sort(key=lambda p: p.arrival_time)
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Starting simulation with {self.scheduler.get_name()}")
            print(f"Cores: {self.num_cores}, Processes: {len(self.all_processes)}")
            print(f"{'='*60}\n")
        
        # Main simulation loop
        process_index = 0
        
        while True:
            # Check if simulation should end
            if max_time is not None and self.current_time >= max_time:
                break
            
            # Check if all processes are complete
            if len(self.completed_processes) >= len(self.all_processes):
                break
            
            # Add newly arrived processes to ready queue
            while process_index < len(self.all_processes):
                process = self.all_processes[process_index]
                if process.arrival_time <= self.current_time:
                    process.state = ProcessState.READY
                    self.ready_queue.append(process)
                    self.scheduler.on_process_arrival(process, self.current_time)
                    process_index += 1
                else:
                    break
            
            # Assign processes to idle cores
            self._assign_processes_to_cores()
            
            # Execute processes on all cores
            min_time_slice = self._execute_all_cores()
            
            # Advance simulation time
            if min_time_slice > 0:
                self.current_time += min_time_slice
            else:
                # No processes running, advance to next arrival
                if process_index < len(self.all_processes):
                    self.current_time = self.all_processes[process_index].arrival_time
                else:
                    break
        
        # Calculate final metrics
        self.metrics = MetricsCollector.calculate_metrics(
            processes=self.all_processes,
            cores=self.cores,
            total_time=self.current_time,
            algorithm_name=self.scheduler.get_name(),
            context_switches=self.total_context_switches
        )
        
        if self.verbose:
            print(f"\n{'='*60}")
            print("Simulation Complete")
            print(f"{'='*60}")
            print(self.metrics)
        
        return self.metrics
    
    def _assign_processes_to_cores(self) -> None:
        """Assign processes from ready queue to idle cores."""
        for core in self.cores:
            if core.is_idle() and self.ready_queue:
                # Ask scheduler to select a process
                selected_process = self.scheduler.select_process(
                    core=core,
                    ready_queue=self.ready_queue,
                    current_time=self.current_time
                )
                
                if selected_process is not None:
                    # Remove from ready queue
                    if selected_process in self.ready_queue:
                        self.ready_queue.remove(selected_process)
                    
                    # Assign to core
                    core.assign_process(selected_process, self.current_time)
                    self.total_context_switches += 1
    
    def _execute_all_cores(self) -> float:
        """
        Execute processes on all cores and return minimum time slice.
        
        Returns:
            Minimum time slice executed across all cores
        """
        time_quantum = self.scheduler.get_time_quantum()
        min_time_slice = float('inf')
        
        for core in self.cores:
            if not core.is_idle():
                current_process = core.get_current_process()
                
                # Check if process should be preempted
                if self.scheduler.should_preempt(current_process, self.ready_queue, self.current_time):
                    preempted = core.preempt_current_process(self.current_time)
                    if preempted and not preempted.is_completed():
                        self.ready_queue.append(preempted)
                    continue
                
                # Execute for time quantum
                actual_time = core.execute_current_process(time_quantum, self.current_time)
                
                if actual_time is not None:
                    min_time_slice = min(min_time_slice, actual_time)
                    
                    # Check if process completed
                    if current_process.is_completed():
                        self.completed_processes.append(current_process)
                        self.scheduler.on_process_completion(current_process, self.current_time + actual_time)
                    else:
                        # Process not complete, return to ready queue if preemptive
                        if self.scheduler.is_preemptive():
                            preempted = core.preempt_current_process(self.current_time + actual_time)
                            if preempted:
                                self.ready_queue.append(preempted)
                                
                                # Special handling for Round Robin queue rotation
                                if hasattr(self.scheduler, 'rotate_queue'):
                                    self.scheduler.rotate_queue(preempted)
        
        return min_time_slice if min_time_slice != float('inf') else 0.0
    
    def _reset_simulation(self) -> None:
        """Reset simulation state."""
        self.current_time = 0.0
        self.ready_queue.clear()
        self.completed_processes.clear()
        self.total_context_switches = 0
        
        # Reset all cores
        for core in self.cores:
            core.reset()
        
        # Reset all processes
        for process in self.all_processes:
            process.state = ProcessState.NEW
            process.remaining_time = process.burst_time
            process.start_time = None
            process.completion_time = None
            process.waiting_time = 0.0
            process.turnaround_time = 0.0
            process.response_time = 0.0
        
        # Reset scheduler
        if self.scheduler:
            self.scheduler.reset()
    
    def get_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the performance metrics from the last simulation."""
        return self.metrics
    
    def display_results(self) -> None:
        """Display detailed simulation results."""
        if self.metrics is None:
            print("No simulation results available. Run simulation first.")
            return
        
        print(f"\n{'='*70}")
        print(f"  SIMULATION RESULTS: {self.scheduler.get_name()}")
        print(f"{'='*70}")
        print(f"\nSystem Configuration:")
        print(f"  Number of Cores: {self.num_cores}")
        print(f"  Total Processes: {len(self.all_processes)}")
        print(f"  Simulation Time: {self.current_time:.2f}ms")
        
        print(f"\nPerformance Metrics:")
        for key, value in self.metrics.to_dict().items():
            if key not in ['Algorithm', 'Cores', 'Processes', 'Simulation Time']:
                print(f"  {key}: {value}")
        
        print(f"\nPer-Core Statistics:")
        for core in self.cores:
            utilization = core.get_utilization(self.current_time)
            print(f"  Core {core.core_id}: {utilization:.2f}% utilized, "
                  f"{core.processes_executed} processes executed")
        
        # Display adaptive scheduler statistics if applicable
        if hasattr(self.scheduler, 'get_algorithm_usage_stats'):
            print(f"\nAdaptive Scheduler Statistics:")
            usage_stats = self.scheduler.get_algorithm_usage_stats()
            for algo, percentage in sorted(usage_stats.items(), key=lambda x: x[1], reverse=True):
                if percentage > 0:
                    print(f"  {algo}: {percentage:.1f}%")
        
        print(f"\n{'='*70}\n")
    
    def plot_results(self) -> None:
        """Generate visualization plots (requires visualization module)."""
        try:
            from visualization.plots import plot_simulation_results
            plot_simulation_results(self)
        except ImportError:
            print("Visualization module not available. Install matplotlib to enable plotting.")

