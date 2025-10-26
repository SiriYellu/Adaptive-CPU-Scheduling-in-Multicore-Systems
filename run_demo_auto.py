"""
AUTOMATED DEMO - Runs all scheduling algorithms and shows results
No user input required - just run and see the output!
"""
import random

# ============================================================================
# SIMPLE PROCESS CLASS
# ============================================================================
class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival_time = arrival
        self.burst_time = burst
        self.remaining_time = burst
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0

# ============================================================================
# SCHEDULING ALGORITHMS
# ============================================================================

def fcfs(processes):
    """First-Come First-Served"""
    time = 0
    for p in sorted(processes, key=lambda x: x.arrival_time):
        time = max(time, p.arrival_time)
        time += p.burst_time
        p.completion_time = time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
    return processes

def sjf(processes):
    """Shortest Job First"""
    time = 0
    completed = []
    remaining = sorted(processes, key=lambda x: x.arrival_time)
    
    while remaining:
        available = [p for p in remaining if p.arrival_time <= time]
        if available:
            p = min(available, key=lambda x: x.burst_time)
            remaining.remove(p)
            time = max(time, p.arrival_time)
            time += p.burst_time
            p.completion_time = time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed.append(p)
        else:
            time = remaining[0].arrival_time
    return completed

def round_robin(processes, quantum=4):
    """Round Robin"""
    time = 0
    queue = []
    remaining = sorted(processes, key=lambda x: x.arrival_time)
    i = 0
    
    if remaining:
        queue.append(remaining[i])
        i += 1
    
    while queue:
        p = queue.pop(0)
        time = max(time, p.arrival_time)
        
        exec_time = min(quantum, p.remaining_time)
        time += exec_time
        p.remaining_time -= exec_time
        
        while i < len(remaining) and remaining[i].arrival_time <= time:
            queue.append(remaining[i])
            i += 1
        
        if p.remaining_time > 0:
            queue.append(p)
        else:
            p.completion_time = time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
    
    return processes

# ============================================================================
# METRICS CALCULATION
# ============================================================================

def show_metrics(processes, name):
    """Calculate and display metrics"""
    n = len(processes)
    avg_tat = sum(p.turnaround_time for p in processes) / n
    avg_wt = sum(p.waiting_time for p in processes) / n
    
    print(f"\n{'='*60}")
    print(f"Algorithm: {name}")
    print(f"{'='*60}")
    print(f"  Processes completed: {n}")
    print(f"  Average Turnaround Time: {avg_tat:.2f} ms")
    print(f"  Average Waiting Time:    {avg_wt:.2f} ms")
    print(f"{'='*60}")
    
    return {'name': name, 'tat': avg_tat, 'wt': avg_wt}

# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    print("\n" + "="*70)
    print(" "*15 + "CPU SCHEDULING SIMULATOR - AUTO DEMO")
    print("="*70)
    
    # Generate sample processes
    random.seed(42)  # For consistent results
    num_processes = 10
    
    print(f"\nGenerating {num_processes} processes...")
    print("-"*70)
    
    base_processes = []
    arrival = 0
    for i in range(num_processes):
        arrival += random.uniform(0, 3)
        burst = random.uniform(5, 25)
        base_processes.append(Process(i, arrival, burst))
        print(f"  P{i}: Arrival={arrival:.1f}ms, Burst={burst:.1f}ms")
    
    print("\n" + "="*70)
    print("RUNNING SCHEDULING ALGORITHMS")
    print("="*70)
    
    results = []
    
    # Test FCFS
    print("\n[1/4] Running FCFS...")
    processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in base_processes]
    fcfs(processes)
    results.append(show_metrics(processes, "FCFS"))
    
    # Test SJF
    print("\n[2/4] Running SJF...")
    processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in base_processes]
    sjf(processes)
    results.append(show_metrics(processes, "SJF"))
    
    # Test Round Robin
    print("\n[3/4] Running Round Robin (q=4ms)...")
    processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in base_processes]
    round_robin(processes, 4)
    results.append(show_metrics(processes, "Round Robin (q=4)"))
    
    # Test Round Robin with different quantum
    print("\n[4/4] Running Round Robin (q=8ms)...")
    processes = [Process(p.pid, p.arrival_time, p.burst_time) for p in base_processes]
    round_robin(processes, 8)
    results.append(show_metrics(processes, "Round Robin (q=8)"))
    
    # Comparison
    print("\n" + "="*70)
    print(" "*20 + "PERFORMANCE COMPARISON")
    print("="*70)
    print(f"\n{'Algorithm':<25} {'Avg TAT (ms)':<15} {'Avg WT (ms)':<15}")
    print("-"*70)
    for r in results:
        print(f"{r['name']:<25} {r['tat']:<15.2f} {r['wt']:<15.2f}")
    
    # Winner
    best_tat = min(results, key=lambda x: x['tat'])
    best_wt = min(results, key=lambda x: x['wt'])
    
    print("\n" + "="*70)
    print("BEST PERFORMERS")
    print("="*70)
    print(f"  Lowest Turnaround Time: {best_tat['name']} ({best_tat['tat']:.2f}ms)")
    print(f"  Lowest Waiting Time:    {best_wt['name']} ({best_wt['wt']:.2f}ms)")
    print("="*70)
    
    # Adaptive logic demo
    print("\n" + "="*70)
    print("ADAPTIVE SCHEDULING DEMONSTRATION")
    print("="*70)
    
    avg_burst = sum(p.burst_time for p in base_processes) / len(base_processes)
    print(f"\nWorkload Analysis:")
    print(f"  Number of processes: {len(base_processes)}")
    print(f"  Average burst time:  {avg_burst:.2f}ms")
    
    if avg_burst < 15:
        selected = "SJF"
        reason = "Short jobs detected -> SJF minimizes waiting time"
    elif len(base_processes) > 20:
        selected = "Round Robin"
        reason = "High load -> RR provides fair time-sharing"
    else:
        selected = "FCFS"
        reason = "Moderate load -> FCFS is simple and efficient"
    
    print(f"\nAdaptive Decision:")
    print(f"  Selected Algorithm: {selected}")
    print(f"  Reason: {reason}")
    
    # Show adaptive result
    adaptive_result = [r for r in results if selected in r['name']]
    if adaptive_result:
        r = adaptive_result[0]
        print(f"\nAdaptive Performance:")
        print(f"  Average Turnaround Time: {r['tat']:.2f}ms")
        print(f"  Average Waiting Time:    {r['wt']:.2f}ms")
    
    print("\n" + "="*70)
    print(" "*25 + "DEMO COMPLETE!")
    print("="*70)
    print("\nAll scheduling algorithms have been demonstrated.")
    print("Results show performance comparison across different strategies.")
    print("\nProject: Adaptive CPU Scheduling in Multicore Systems")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

