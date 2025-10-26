"""
SIMPLIFIED CPU SCHEDULING SIMULATOR
All-in-one file for easy execution and demonstration
"""
import random
import time
from collections import deque

# ============================================================================
# PROCESS CLASS
# ============================================================================
class Process:
    def __init__(self, pid, arrival, burst, priority=5):
        self.pid = pid
        self.arrival_time = arrival
        self.burst_time = burst
        self.remaining_time = burst
        self.priority = priority
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
    
    def __repr__(self):
        return f"P{self.pid}"


# ============================================================================
# SCHEDULING ALGORITHMS
# ============================================================================

def fcfs_schedule(processes):
    """First-Come First-Served Scheduling"""
    print("\n" + "="*60)
    print("FCFS (First-Come, First-Served) Scheduling")
    print("="*60)
    
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    completed = []
    
    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        
        p.start_time = current_time
        p.completion_time = current_time + p.burst_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        
        print(f"  Time {current_time:3.0f}: {p} starts (burst={p.burst_time:.0f}ms)")
        current_time = p.completion_time
        completed.append(p)
    
    return completed


def sjf_schedule(processes):
    """Shortest Job First Scheduling"""
    print("\n" + "="*60)
    print("SJF (Shortest Job First) Scheduling")
    print("="*60)
    
    processes.sort(key=lambda p: (p.arrival_time, p.burst_time))
    current_time = 0
    ready_queue = []
    completed = []
    remaining = processes.copy()
    
    while remaining or ready_queue:
        # Add arrived processes to ready queue
        while remaining and remaining[0].arrival_time <= current_time:
            ready_queue.append(remaining.pop(0))
        
        if ready_queue:
            # Sort by burst time (shortest first)
            ready_queue.sort(key=lambda p: p.burst_time)
            p = ready_queue.pop(0)
            
            p.start_time = current_time
            p.completion_time = current_time + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            
            print(f"  Time {current_time:3.0f}: {p} starts (burst={p.burst_time:.0f}ms)")
            current_time = p.completion_time
            completed.append(p)
        else:
            current_time = remaining[0].arrival_time if remaining else current_time
    
    return completed


def round_robin_schedule(processes, quantum=4):
    """Round Robin Scheduling"""
    print("\n" + "="*60)
    print(f"Round Robin Scheduling (Quantum = {quantum}ms)")
    print("="*60)
    
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    queue = deque()
    completed = []
    remaining = processes.copy()
    
    # Add first process
    if remaining:
        queue.append(remaining.pop(0))
    
    while queue or remaining:
        # Add newly arrived processes
        while remaining and remaining[0].arrival_time <= current_time:
            queue.append(remaining.pop(0))
        
        if queue:
            p = queue.popleft()
            
            if p.start_time is None:
                p.start_time = current_time
            
            execute_time = min(quantum, p.remaining_time)
            print(f"  Time {current_time:3.0f}: {p} executes for {execute_time:.0f}ms (remaining={p.remaining_time:.0f}ms)")
            
            current_time += execute_time
            p.remaining_time -= execute_time
            
            # Add newly arrived during execution
            while remaining and remaining[0].arrival_time <= current_time:
                queue.append(remaining.pop(0))
            
            if p.remaining_time > 0:
                queue.append(p)  # Back to queue
            else:
                p.completion_time = current_time
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                completed.append(p)
        else:
            if remaining:
                current_time = remaining[0].arrival_time
    
    return completed


def adaptive_schedule(processes):
    """Adaptive Scheduling - Selects best algorithm based on workload"""
    print("\n" + "="*60)
    print("ADAPTIVE Scheduling (Intelligent Selection)")
    print("="*60)
    
    # Analyze workload
    avg_burst = sum(p.burst_time for p in processes) / len(processes)
    num_processes = len(processes)
    
    print(f"\n  Analyzing workload:")
    print(f"    Processes: {num_processes}")
    print(f"    Avg Burst Time: {avg_burst:.1f}ms")
    
    # Decision logic
    if avg_burst < 15:
        print(f"  → Short jobs detected → Using SJF")
        algorithm = "SJF"
        completed = sjf_schedule(processes)
    elif num_processes > 15:
        print(f"  → High load detected → Using Round Robin")
        algorithm = "Round Robin"
        completed = round_robin_schedule(processes, quantum=5)
    else:
        print(f"  → Balanced load → Using FCFS")
        algorithm = "FCFS"
        completed = fcfs_schedule(processes)
    
    return completed, algorithm


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

def calculate_metrics(processes, algorithm_name):
    """Calculate and display performance metrics"""
    n = len(processes)
    
    avg_turnaround = sum(p.turnaround_time for p in processes) / n
    avg_waiting = sum(p.waiting_time for p in processes) / n
    total_time = max(p.completion_time for p in processes)
    total_burst = sum(p.burst_time for p in processes)
    cpu_util = (total_burst / total_time * 100) if total_time > 0 else 0
    throughput = (n / total_time * 1000) if total_time > 0 else 0
    
    print("\n" + "-"*60)
    print(f"Performance Metrics for {algorithm_name}:")
    print("-"*60)
    print(f"  Average Turnaround Time: {avg_turnaround:.2f} ms")
    print(f"  Average Waiting Time:    {avg_waiting:.2f} ms")
    print(f"  CPU Utilization:         {cpu_util:.2f} %")
    print(f"  Throughput:              {throughput:.2f} processes/sec")
    print(f"  Total Simulation Time:   {total_time:.2f} ms")
    print("-"*60)
    
    return {
        'algorithm': algorithm_name,
        'avg_turnaround': avg_turnaround,
        'avg_waiting': avg_waiting,
        'cpu_util': cpu_util,
        'throughput': throughput
    }


# ============================================================================
# PROCESS GENERATION
# ============================================================================

def generate_processes(num=10, workload='mixed'):
    """Generate random processes"""
    processes = []
    current_time = 0
    
    for i in range(num):
        arrival = current_time + random.uniform(0, 5)
        
        if workload == 'short':
            burst = random.uniform(5, 15)
        elif workload == 'long':
            burst = random.uniform(20, 50)
        else:  # mixed
            burst = random.uniform(5, 40)
        
        priority = random.randint(1, 10)
        processes.append(Process(i, arrival, burst, priority))
        current_time = arrival
    
    return processes


# ============================================================================
# MAIN DEMO
# ============================================================================

def demo_single_algorithm():
    """Demonstrate a single algorithm"""
    print("\n" + "="*60)
    print("DEMO 1: Single Algorithm Demonstration")
    print("="*60)
    
    processes = generate_processes(8, 'mixed')
    
    print("\nGenerated Processes:")
    print("-"*60)
    for p in processes:
        print(f"  {p}: Arrival={p.arrival_time:.1f}ms, Burst={p.burst_time:.1f}ms, Priority={p.priority}")
    
    # Run FCFS
    procs_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    completed = fcfs_schedule(procs_copy)
    calculate_metrics(completed, "FCFS")
    
    print("\n[Press Enter to continue...]")
    input()


def demo_comparison():
    """Compare all algorithms"""
    print("\n" + "="*60)
    print("DEMO 2: Algorithm Comparison")
    print("="*60)
    
    processes = generate_processes(12, 'mixed')
    
    print("\nGenerated Processes:")
    print("-"*60)
    for p in processes:
        print(f"  {p}: Arrival={p.arrival_time:.1f}ms, Burst={p.burst_time:.1f}ms")
    
    results = []
    
    # Test each algorithm
    algorithms = [
        ('FCFS', lambda p: fcfs_schedule(p)),
        ('SJF', lambda p: sjf_schedule(p)),
        ('Round Robin (q=4)', lambda p: round_robin_schedule(p, 4)),
    ]
    
    for name, algo_func in algorithms:
        procs_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
        completed = algo_func(procs_copy)
        metrics = calculate_metrics(completed, name)
        results.append(metrics)
        print("\n[Press Enter for next algorithm...]")
        input()
    
    # Summary comparison
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"{'Algorithm':<20} {'Avg TAT':<12} {'Avg WT':<12} {'CPU Util':<12}")
    print("-"*60)
    for r in results:
        print(f"{r['algorithm']:<20} {r['avg_turnaround']:<12.2f} {r['avg_waiting']:<12.2f} {r['cpu_util']:<12.2f}")
    print("="*60)
    
    # Find best
    best_tat = min(results, key=lambda x: x['avg_turnaround'])
    best_wait = min(results, key=lambda x: x['avg_waiting'])
    
    print(f"\nBest Turnaround Time: {best_tat['algorithm']}")
    print(f"Best Waiting Time:    {best_wait['algorithm']}")


def demo_adaptive():
    """Demonstrate adaptive scheduling"""
    print("\n" + "="*60)
    print("DEMO 3: Adaptive Scheduling")
    print("="*60)
    
    workloads = [
        ('Short Jobs', 'short', 15),
        ('Long Jobs', 'long', 10),
        ('Mixed Jobs', 'mixed', 20)
    ]
    
    for workload_name, workload_type, num_procs in workloads:
        print(f"\n{'='*60}")
        print(f"Testing with: {workload_name} ({num_procs} processes)")
        print(f"{'='*60}")
        
        processes = generate_processes(num_procs, workload_type)
        procs_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
        
        completed, selected_algo = adaptive_schedule(procs_copy)
        calculate_metrics(completed, f"Adaptive → {selected_algo}")
        
        print("\n[Press Enter for next workload...]")
        input()


def main_menu():
    """Main interactive menu"""
    while True:
        print("\n" + "="*60)
        print("ADAPTIVE CPU SCHEDULING SIMULATOR")
        print("="*60)
        print("\nSelect Demo:")
        print("  1. Single Algorithm Demo (FCFS)")
        print("  2. Compare All Algorithms")
        print("  3. Adaptive Scheduling Demo")
        print("  4. Quick Test (All at once)")
        print("  5. Exit")
        print("-"*60)
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            demo_single_algorithm()
        elif choice == '2':
            demo_comparison()
        elif choice == '3':
            demo_adaptive()
        elif choice == '4':
            print("\n" + "="*60)
            print("QUICK TEST - Running All Demos")
            print("="*60)
            
            # Quick run without pauses
            processes = generate_processes(10, 'mixed')
            
            print("\nTesting FCFS...")
            p1 = [Process(p.pid, p.arrival_time, p.burst_time) for p in processes]
            fcfs_schedule(p1)
            calculate_metrics(p1, "FCFS")
            
            print("\nTesting SJF...")
            p2 = [Process(p.pid, p.arrival_time, p.burst_time) for p in processes]
            sjf_schedule(p2)
            calculate_metrics(p2, "SJF")
            
            print("\nTesting Round Robin...")
            p3 = [Process(p.pid, p.arrival_time, p.burst_time) for p in processes]
            round_robin_schedule(p3, 4)
            calculate_metrics(p3, "Round Robin")
            
            print("\n✓ All tests completed!")
            input("\nPress Enter to return to menu...")
            
        elif choice == '5':
            print("\n" + "="*60)
            print("Thank you for using the CPU Scheduler!")
            print("="*60)
            break
        else:
            print("\n❌ Invalid choice! Please enter 1-5.")


# ============================================================================
# RUN THE DEMO
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("="*60)
    print("   ADAPTIVE CPU SCHEDULING SIMULATOR - SIMPLE DEMO")
    print("="*60)
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

