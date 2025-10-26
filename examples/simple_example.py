"""
Simple example demonstrating basic usage of the scheduler simulator.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scheduler_simulator import MulticoreSchedulerSimulator
from algorithms.adaptive_scheduler import AdaptiveScheduler
from algorithms.round_robin import RoundRobinScheduler
from algorithms.load_balancing import LoadBalancingScheduler


def simple_adaptive_example():
    """Simple example using adaptive scheduler."""
    print("\n=== Simple Adaptive Scheduler Example ===\n")
    
    # Create a simulator with 4 cores
    simulator = MulticoreSchedulerSimulator(num_cores=4, verbose=True)
    
    # Use adaptive scheduler
    scheduler = AdaptiveScheduler(num_cores=4)
    simulator.set_scheduler(scheduler)
    
    # Generate 20 processes
    simulator.generate_processes(
        num_processes=20,
        workload_type='mixed'
    )
    
    # Run simulation
    metrics = simulator.run_simulation()
    
    # Display results
    simulator.display_results()
    
    # Try to show plots
    try:
        simulator.plot_results()
    except:
        print("Plotting not available")


def simple_round_robin_example():
    """Simple example using round robin scheduler."""
    print("\n=== Simple Round Robin Example ===\n")
    
    # Create simulator
    simulator = MulticoreSchedulerSimulator(num_cores=2, verbose=True)
    
    # Use Round Robin with time quantum of 5ms
    scheduler = RoundRobinScheduler(num_cores=2, time_quantum=5.0)
    simulator.set_scheduler(scheduler)
    
    # Generate processes
    simulator.generate_processes(
        num_processes=10,
        min_burst=10.0,
        max_burst=30.0,
        workload_type='cpu_bound'
    )
    
    # Run and display
    simulator.run_simulation()
    simulator.display_results()


def simple_load_balancing_example():
    """Simple example using load balancing scheduler."""
    print("\n=== Simple Load Balancing Example ===\n")
    
    # Create simulator with 6 cores
    simulator = MulticoreSchedulerSimulator(num_cores=6, verbose=True)
    
    # Use Load Balancing
    scheduler = LoadBalancingScheduler(num_cores=6)
    simulator.set_scheduler(scheduler)
    
    # Generate CPU-intensive workload
    simulator.generate_processes(
        num_processes=30,
        workload_type='cpu_bound'
    )
    
    # Run and display
    simulator.run_simulation()
    simulator.display_results()


if __name__ == "__main__":
    # Run all examples
    simple_adaptive_example()
    
    input("\nPress Enter to continue to next example...")
    simple_round_robin_example()
    
    input("\nPress Enter to continue to next example...")
    simple_load_balancing_example()
    
    print("\n\nAll examples completed!")

