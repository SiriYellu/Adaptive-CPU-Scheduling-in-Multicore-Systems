"""
Interactive demo of the Adaptive CPU Scheduling system.
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
from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama for colored output
init(autoreset=True)


def print_header(text):
    """Print a styled header."""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{text.center(80)}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")


def print_section(text):
    """Print a section header."""
    print(f"\n{Fore.YELLOW}{'─'*80}")
    print(f"{Fore.YELLOW}{text}")
    print(f"{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}\n")


def demo_adaptive_scheduler():
    """Demonstrate the adaptive scheduler with a mixed workload."""
    print_header("ADAPTIVE SCHEDULER DEMO")
    
    print(f"{Fore.GREEN}This demo shows how the Adaptive Scheduler automatically selects")
    print(f"{Fore.GREEN}the best scheduling algorithm based on system state and workload.{Style.RESET_ALL}\n")
    
    # Create simulator with 4 cores
    num_cores = 4
    simulator = MulticoreSchedulerSimulator(num_cores=num_cores, verbose=False)
    
    # Create adaptive scheduler
    scheduler = AdaptiveScheduler(num_cores=num_cores, adaptation_interval=30.0)
    simulator.set_scheduler(scheduler)
    
    # Generate mixed workload
    print(f"{Fore.MAGENTA}Generating 50 processes with mixed workload characteristics...{Style.RESET_ALL}")
    simulator.generate_processes(
        num_processes=50,
        arrival_rate=3.0,
        min_burst=5.0,
        max_burst=60.0,
        workload_type='mixed'
    )
    
    # Run simulation
    print(f"\n{Fore.MAGENTA}Running simulation...{Style.RESET_ALL}\n")
    metrics = simulator.run_simulation()
    
    # Display results
    simulator.display_results()
    
    # Show algorithm usage
    if hasattr(scheduler, 'get_algorithm_usage_stats'):
        print_section("Adaptive Scheduler Algorithm Selection")
        usage_stats = scheduler.get_algorithm_usage_stats()
        
        table_data = [[algo, f"{percentage:.1f}%"] 
                     for algo, percentage in sorted(usage_stats.items(), 
                                                    key=lambda x: x[1], 
                                                    reverse=True)
                     if percentage > 0]
        
        print(tabulate(table_data, headers=['Algorithm', 'Usage %'], tablefmt='grid'))
    
    # Try to plot
    try:
        print(f"\n{Fore.CYAN}Generating visualization plots...{Style.RESET_ALL}")
        simulator.plot_results()
    except Exception as e:
        print(f"{Fore.RED}Visualization not available: {e}{Style.RESET_ALL}")


def demo_single_algorithm(algorithm_name, scheduler):
    """Demo a single scheduling algorithm."""
    print_section(f"Testing: {algorithm_name}")
    
    num_cores = 4
    simulator = MulticoreSchedulerSimulator(num_cores=num_cores, verbose=False)
    simulator.set_scheduler(scheduler)
    
    # Generate workload
    simulator.generate_processes(
        num_processes=30,
        arrival_rate=4.0,
        min_burst=5.0,
        max_burst=40.0,
        workload_type='mixed'
    )
    
    # Run simulation
    metrics = simulator.run_simulation()
    
    # Display key metrics
    print(f"{Fore.GREEN}Results for {algorithm_name}:{Style.RESET_ALL}")
    print(f"  Avg Turnaround Time: {metrics.average_turnaround_time:.2f}ms")
    print(f"  Avg Waiting Time: {metrics.average_waiting_time:.2f}ms")
    print(f"  CPU Utilization: {metrics.cpu_utilization:.2f}%")
    print(f"  Throughput: {metrics.throughput:.2f} processes/sec")
    print(f"  Load Balance Score: {metrics.load_balance_score:.2f}")
    
    return metrics


def demo_all_algorithms():
    """Compare all scheduling algorithms."""
    print_header("ALGORITHM COMPARISON DEMO")
    
    num_cores = 4
    
    # Define all algorithms
    algorithms = {
        'FCFS': FCFSScheduler(num_cores),
        'SJF (Preemptive)': SJFScheduler(num_cores, preemptive=True),
        'Round Robin': RoundRobinScheduler(num_cores, time_quantum=5.0),
        'Priority': PriorityScheduler(num_cores, preemptive=True),
        'Load Balancing': LoadBalancingScheduler(num_cores),
        'Work Stealing': WorkStealingScheduler(num_cores),
        'Adaptive': AdaptiveScheduler(num_cores)
    }
    
    results = {}
    
    print(f"{Fore.MAGENTA}Running simulations for all algorithms...{Style.RESET_ALL}\n")
    
    for name, scheduler in algorithms.items():
        metrics = demo_single_algorithm(name, scheduler)
        results[name] = metrics
    
    # Create comparison table
    print_section("ALGORITHM COMPARISON SUMMARY")
    
    table_data = []
    for name, metrics in results.items():
        table_data.append([
            name,
            f"{metrics.average_turnaround_time:.2f}",
            f"{metrics.average_waiting_time:.2f}",
            f"{metrics.cpu_utilization:.2f}",
            f"{metrics.throughput:.2f}",
            f"{metrics.load_balance_score:.2f}"
        ])
    
    headers = ['Algorithm', 'Avg Turnaround', 'Avg Waiting', 'CPU Util %', 'Throughput', 'Load Balance']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Find best performers
    print_section("BEST PERFORMERS")
    
    best_turnaround = min(results.items(), key=lambda x: x[1].average_turnaround_time)
    best_waiting = min(results.items(), key=lambda x: x[1].average_waiting_time)
    best_utilization = max(results.items(), key=lambda x: x[1].cpu_utilization)
    best_throughput = max(results.items(), key=lambda x: x[1].throughput)
    best_balance = max(results.items(), key=lambda x: x[1].load_balance_score)
    
    print(f"{Fore.GREEN}Best Turnaround Time: {best_turnaround[0]} ({best_turnaround[1].average_turnaround_time:.2f}ms)")
    print(f"{Fore.GREEN}Best Waiting Time: {best_waiting[0]} ({best_waiting[1].average_waiting_time:.2f}ms)")
    print(f"{Fore.GREEN}Best CPU Utilization: {best_utilization[0]} ({best_utilization[1].cpu_utilization:.2f}%)")
    print(f"{Fore.GREEN}Best Throughput: {best_throughput[0]} ({best_throughput[1].throughput:.2f} proc/sec)")
    print(f"{Fore.GREEN}Best Load Balance: {best_balance[0]} ({best_balance[1].load_balance_score:.2f}){Style.RESET_ALL}")
    
    return results


def demo_workload_types():
    """Compare adaptive scheduler performance on different workload types."""
    print_header("WORKLOAD-SPECIFIC PERFORMANCE")
    
    num_cores = 4
    workload_types = ['cpu_bound', 'io_bound', 'mixed']
    
    results = {}
    
    for workload in workload_types:
        print_section(f"Testing with {workload.upper().replace('_', ' ')} workload")
        
        simulator = MulticoreSchedulerSimulator(num_cores=num_cores, verbose=False)
        scheduler = AdaptiveScheduler(num_cores=num_cores)
        simulator.set_scheduler(scheduler)
        
        simulator.generate_processes(
            num_processes=40,
            arrival_rate=3.0,
            min_burst=5.0,
            max_burst=50.0,
            workload_type=workload
        )
        
        metrics = simulator.run_simulation()
        results[workload] = metrics
        
        print(f"{Fore.GREEN}Results for {workload} workload:{Style.RESET_ALL}")
        print(f"  Avg Turnaround Time: {metrics.average_turnaround_time:.2f}ms")
        print(f"  CPU Utilization: {metrics.cpu_utilization:.2f}%")
        print(f"  Load Balance Score: {metrics.load_balance_score:.2f}")
    
    # Summary table
    print_section("WORKLOAD COMPARISON SUMMARY")
    
    table_data = []
    for workload, metrics in results.items():
        table_data.append([
            workload.replace('_', ' ').title(),
            f"{metrics.average_turnaround_time:.2f}",
            f"{metrics.average_waiting_time:.2f}",
            f"{metrics.cpu_utilization:.2f}",
            f"{metrics.load_balance_score:.2f}"
        ])
    
    headers = ['Workload Type', 'Avg Turnaround', 'Avg Waiting', 'CPU Util %', 'Load Balance']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def main_menu():
    """Display main menu and handle user selection."""
    while True:
        print_header("ADAPTIVE CPU SCHEDULING SIMULATOR")
        
        print(f"{Fore.CYAN}Select a demo to run:{Style.RESET_ALL}\n")
        print(f"  {Fore.WHITE}1. Adaptive Scheduler Demo{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}2. Compare All Algorithms{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}3. Workload-Specific Performance{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}4. Run All Demos{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}5. Exit{Style.RESET_ALL}\n")
        
        choice = input(f"{Fore.YELLOW}Enter your choice (1-5): {Style.RESET_ALL}")
        
        if choice == '1':
            demo_adaptive_scheduler()
        elif choice == '2':
            demo_all_algorithms()
        elif choice == '3':
            demo_workload_types()
        elif choice == '4':
            demo_adaptive_scheduler()
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            demo_all_algorithms()
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            demo_workload_types()
        elif choice == '5':
            print(f"\n{Fore.GREEN}Thank you for using the Adaptive CPU Scheduling Simulator!{Style.RESET_ALL}\n")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Demo interrupted by user.{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()

