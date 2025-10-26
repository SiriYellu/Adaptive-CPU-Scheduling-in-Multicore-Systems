"""
Compare different scheduling algorithms on the same workload.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scheduler_simulator import MulticoreSchedulerSimulator
from algorithms.adaptive_scheduler import AdaptiveScheduler
from algorithms.fcfs import FCFSScheduler
from algorithms.sjf import SJFScheduler
from algorithms.round_robin import RoundRobinScheduler
from algorithms.priority import PriorityScheduler
from algorithms.load_balancing import LoadBalancingScheduler
from algorithms.work_stealing import WorkStealingScheduler
from core.process import Process
from typing import Dict, List
import random


def compare_all_algorithms(
    num_cores: int = 4,
    num_processes: int = 50,
    workload_type: str = 'mixed',
    seed: int = 42
) -> Dict:
    """
    Compare all scheduling algorithms on the same workload.
    
    Args:
        num_cores: Number of CPU cores
        num_processes: Number of processes to simulate
        workload_type: Type of workload ('cpu_bound', 'io_bound', 'mixed')
        seed: Random seed for reproducible results
        
    Returns:
        Dictionary with results for each algorithm
    """
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Generate a common set of processes
    print(f"Generating {num_processes} processes with {workload_type} workload...")
    base_simulator = MulticoreSchedulerSimulator(num_cores=num_cores, verbose=False)
    base_simulator.generate_processes(
        num_processes=num_processes,
        arrival_rate=4.0,
        min_burst=5.0,
        max_burst=50.0,
        workload_type=workload_type
    )
    
    # Store the generated processes
    common_processes = [
        Process(
            pid=p.pid,
            arrival_time=p.arrival_time,
            burst_time=p.burst_time,
            priority=p.priority,
            process_type=p.process_type
        )
        for p in base_simulator.all_processes
    ]
    
    # Define all algorithms to test
    algorithms = {
        'FCFS': FCFSScheduler(num_cores),
        'SJF (Non-preemptive)': SJFScheduler(num_cores, preemptive=False),
        'SJF (Preemptive)': SJFScheduler(num_cores, preemptive=True),
        'Round Robin (q=4)': RoundRobinScheduler(num_cores, time_quantum=4.0),
        'Round Robin (q=8)': RoundRobinScheduler(num_cores, time_quantum=8.0),
        'Priority (Non-preemptive)': PriorityScheduler(num_cores, preemptive=False),
        'Priority (Preemptive)': PriorityScheduler(num_cores, preemptive=True),
        'Load Balancing': LoadBalancingScheduler(num_cores),
        'Work Stealing': WorkStealingScheduler(num_cores),
        'Adaptive': AdaptiveScheduler(num_cores)
    }
    
    results = {}
    
    print(f"\nRunning simulations with {num_cores} cores...\n")
    print(f"{'Algorithm':<30} {'Status':<15}")
    print("-" * 45)
    
    for name, scheduler in algorithms.items():
        # Create new simulator for each algorithm
        simulator = MulticoreSchedulerSimulator(num_cores=num_cores, verbose=False)
        simulator.set_scheduler(scheduler)
        
        # Add copies of the common processes
        for p in common_processes:
            new_process = Process(
                pid=p.pid,
                arrival_time=p.arrival_time,
                burst_time=p.burst_time,
                priority=p.priority,
                process_type=p.process_type
            )
            simulator.add_process(new_process)
        
        # Run simulation
        try:
            metrics = simulator.run_simulation()
            results[name] = {
                'metrics': metrics,
                'simulator': simulator
            }
            print(f"{name:<30} {'✓ Complete':<15}")
        except Exception as e:
            print(f"{name:<30} {'✗ Failed':<15} - {str(e)}")
    
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80 + "\n")
    
    # Print comparison table
    print(f"{'Algorithm':<30} {'Turnaround':<12} {'Waiting':<12} {'CPU Util':<12} {'Throughput':<12} {'Load Bal':<10}")
    print("-" * 98)
    
    for name, result in results.items():
        metrics = result['metrics']
        print(f"{name:<30} "
              f"{metrics.average_turnaround_time:<12.2f} "
              f"{metrics.average_waiting_time:<12.2f} "
              f"{metrics.cpu_utilization:<12.2f} "
              f"{metrics.throughput:<12.2f} "
              f"{metrics.load_balance_score:<10.2f}")
    
    # Find best algorithms for each metric
    print("\n" + "="*80)
    print("BEST PERFORMERS")
    print("="*80 + "\n")
    
    best_turnaround = min(results.items(), key=lambda x: x[1]['metrics'].average_turnaround_time)
    best_waiting = min(results.items(), key=lambda x: x[1]['metrics'].average_waiting_time)
    best_cpu = max(results.items(), key=lambda x: x[1]['metrics'].cpu_utilization)
    best_throughput = max(results.items(), key=lambda x: x[1]['metrics'].throughput)
    best_balance = max(results.items(), key=lambda x: x[1]['metrics'].load_balance_score)
    
    print(f"Lowest Turnaround Time:  {best_turnaround[0]:<30} {best_turnaround[1]['metrics'].average_turnaround_time:.2f}ms")
    print(f"Lowest Waiting Time:     {best_waiting[0]:<30} {best_waiting[1]['metrics'].average_waiting_time:.2f}ms")
    print(f"Highest CPU Utilization: {best_cpu[0]:<30} {best_cpu[1]['metrics'].cpu_utilization:.2f}%")
    print(f"Highest Throughput:      {best_throughput[0]:<30} {best_throughput[1]['metrics'].throughput:.2f} proc/sec")
    print(f"Best Load Balance:       {best_balance[0]:<30} {best_balance[1]['metrics'].load_balance_score:.2f}")
    
    # Try to create comparison plot
    try:
        from visualization.plots import compare_algorithms_plot
        print("\nGenerating comparison plots...")
        compare_algorithms_plot(results)
    except ImportError:
        print("\nVisualization module not available. Install matplotlib to see plots.")
    except Exception as e:
        print(f"\nCould not generate plots: {e}")
    
    return results


def compare_workload_types(num_cores: int = 4, num_processes: int = 40) -> Dict:
    """
    Compare adaptive scheduler performance across different workload types.
    
    Args:
        num_cores: Number of CPU cores
        num_processes: Number of processes per workload
        
    Returns:
        Dictionary with results for each workload type
    """
    workload_types = ['cpu_bound', 'io_bound', 'mixed']
    results = {}
    
    print("="*80)
    print("WORKLOAD TYPE COMPARISON")
    print("="*80 + "\n")
    
    for workload in workload_types:
        print(f"Testing {workload} workload...")
        
        # Test adaptive scheduler
        simulator = MulticoreSchedulerSimulator(num_cores=num_cores, verbose=False)
        scheduler = AdaptiveScheduler(num_cores=num_cores)
        simulator.set_scheduler(scheduler)
        
        simulator.generate_processes(
            num_processes=num_processes,
            workload_type=workload
        )
        
        metrics = simulator.run_simulation()
        results[workload] = {
            'Adaptive': {
                'metrics': metrics,
                'simulator': simulator
            }
        }
    
    # Print results
    print("\n" + "="*80)
    print("RESULTS BY WORKLOAD TYPE")
    print("="*80 + "\n")
    
    print(f"{'Workload Type':<20} {'Turnaround':<12} {'Waiting':<12} {'CPU Util':<12} {'Load Bal':<10}")
    print("-" * 66)
    
    for workload, algos in results.items():
        for algo_name, result in algos.items():
            metrics = result['metrics']
            print(f"{workload:<20} "
                  f"{metrics.average_turnaround_time:<12.2f} "
                  f"{metrics.average_waiting_time:<12.2f} "
                  f"{metrics.cpu_utilization:<12.2f} "
                  f"{metrics.load_balance_score:<10.2f}")
    
    return results


if __name__ == "__main__":
    print("="*80)
    print("CPU SCHEDULING ALGORITHM COMPARISON")
    print("="*80 + "\n")
    
    # Compare all algorithms
    results = compare_all_algorithms(
        num_cores=4,
        num_processes=50,
        workload_type='mixed'
    )
    
    print("\n")
    input("Press Enter to continue to workload comparison...")
    print("\n")
    
    # Compare workload types
    workload_results = compare_workload_types(
        num_cores=4,
        num_processes=40
    )
    
    print("\n\nComparison complete!")

