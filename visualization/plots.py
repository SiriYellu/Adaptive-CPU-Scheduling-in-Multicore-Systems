"""
Visualization tools for scheduling simulation results.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from typing import List, Dict, Any
import seaborn as sns


# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10


def plot_simulation_results(simulator) -> None:
    """
    Create comprehensive visualization of simulation results.
    
    Args:
        simulator: MulticoreSchedulerSimulator instance with completed simulation
    """
    if simulator.metrics is None:
        print("No simulation results to plot. Run simulation first.")
        return
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Gantt Chart (top row, spans all columns)
    ax_gantt = fig.add_subplot(gs[0, :])
    _plot_gantt_chart(ax_gantt, simulator)
    
    # 2. Performance Metrics Comparison
    ax_metrics = fig.add_subplot(gs[1, 0])
    _plot_performance_bars(ax_metrics, simulator.metrics)
    
    # 3. Core Utilization
    ax_util = fig.add_subplot(gs[1, 1])
    _plot_core_utilization(ax_util, simulator.cores, simulator.current_time)
    
    # 4. Process Turnaround Times
    ax_turnaround = fig.add_subplot(gs[1, 2])
    _plot_turnaround_times(ax_turnaround, simulator.completed_processes)
    
    # 5. Waiting Time Distribution
    ax_waiting = fig.add_subplot(gs[2, 0])
    _plot_waiting_time_distribution(ax_waiting, simulator.completed_processes)
    
    # 6. Algorithm Usage (if adaptive)
    ax_algo = fig.add_subplot(gs[2, 1])
    if hasattr(simulator.scheduler, 'get_algorithm_usage_stats'):
        _plot_algorithm_usage(ax_algo, simulator.scheduler)
    else:
        ax_algo.text(0.5, 0.5, 'Adaptive Scheduler\nStats Not Available', 
                    ha='center', va='center', fontsize=12)
        ax_algo.axis('off')
    
    # 7. Load Balance Over Time
    ax_load = fig.add_subplot(gs[2, 2])
    _plot_load_balance(ax_load, simulator.cores)
    
    # Main title
    fig.suptitle(f'CPU Scheduling Simulation Results - {simulator.scheduler.get_name()}',
                 fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def _plot_gantt_chart(ax, simulator) -> None:
    """Plot Gantt chart showing process execution timeline."""
    ax.set_title('Process Execution Timeline (Gantt Chart)', fontweight='bold')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('CPU Core')
    
    # Color map for processes
    colors = plt.cm.tab20(np.linspace(0, 1, len(simulator.all_processes)))
    process_colors = {p.pid: colors[i] for i, p in enumerate(simulator.all_processes)}
    
    # Track execution intervals for each core
    # We'll need to re-simulate or track this during simulation
    # For now, show a simplified version based on completion times
    
    y_ticks = []
    y_labels = []
    
    for core in simulator.cores:
        y_ticks.append(core.core_id)
        y_labels.append(f'Core {core.core_id}')
    
    # Plot process bars (simplified - showing final execution)
    for process in simulator.completed_processes:
        if process.start_time is not None and process.completion_time is not None:
            core_id = process.executed_on_core if process.executed_on_core is not None else 0
            start = process.start_time
            duration = process.completion_time - process.start_time
            
            ax.barh(core_id, duration, left=start, height=0.6,
                   color=process_colors[process.pid], alpha=0.8,
                   edgecolor='black', linewidth=0.5)
            
            # Add process ID label
            if duration > 2:  # Only show label if bar is wide enough
                ax.text(start + duration/2, core_id, f'P{process.pid}',
                       ha='center', va='center', fontsize=8, fontweight='bold')
    
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.grid(True, alpha=0.3)


def _plot_performance_bars(ax, metrics) -> None:
    """Plot key performance metrics as bar chart."""
    ax.set_title('Key Performance Metrics', fontweight='bold')
    
    metric_names = ['Avg Turnaround', 'Avg Waiting', 'Avg Response']
    values = [
        metrics.average_turnaround_time,
        metrics.average_waiting_time,
        metrics.average_response_time
    ]
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    bars = ax.bar(metric_names, values, color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:.2f}ms', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Time (ms)')
    ax.grid(True, alpha=0.3, axis='y')


def _plot_core_utilization(ax, cores, total_time) -> None:
    """Plot CPU core utilization as bar chart."""
    ax.set_title('CPU Core Utilization', fontweight='bold')
    
    core_ids = [f'Core {core.core_id}' for core in cores]
    utilizations = [core.get_utilization(total_time) for core in cores]
    
    colors = ['#27ae60' if u > 70 else '#f39c12' if u > 40 else '#e74c3c' for u in utilizations]
    bars = ax.bar(core_ids, utilizations, color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels
    for bar, value in zip(bars, utilizations):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Utilization (%)')
    ax.set_ylim(0, 110)
    ax.axhline(y=100, color='r', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3, axis='y')


def _plot_turnaround_times(ax, processes) -> None:
    """Plot turnaround times for all processes."""
    ax.set_title('Process Turnaround Times', fontweight='bold')
    
    pids = [p.pid for p in sorted(processes, key=lambda x: x.pid)]
    turnaround_times = [p.turnaround_time for p in sorted(processes, key=lambda x: x.pid)]
    
    ax.scatter(pids, turnaround_times, alpha=0.6, s=50, color='#9b59b6')
    ax.plot(pids, turnaround_times, alpha=0.3, color='#9b59b6')
    
    # Add average line
    avg_turnaround = np.mean(turnaround_times)
    ax.axhline(y=avg_turnaround, color='r', linestyle='--', 
               label=f'Average: {avg_turnaround:.2f}ms')
    
    ax.set_xlabel('Process ID')
    ax.set_ylabel('Turnaround Time (ms)')
    ax.legend()
    ax.grid(True, alpha=0.3)


def _plot_waiting_time_distribution(ax, processes) -> None:
    """Plot distribution of waiting times."""
    ax.set_title('Waiting Time Distribution', fontweight='bold')
    
    waiting_times = [p.waiting_time for p in processes]
    
    ax.hist(waiting_times, bins=15, color='#e67e22', alpha=0.7, edgecolor='black')
    
    # Add mean and median lines
    mean_wait = np.mean(waiting_times)
    median_wait = np.median(waiting_times)
    
    ax.axvline(mean_wait, color='r', linestyle='--', linewidth=2, label=f'Mean: {mean_wait:.2f}ms')
    ax.axvline(median_wait, color='g', linestyle='--', linewidth=2, label=f'Median: {median_wait:.2f}ms')
    
    ax.set_xlabel('Waiting Time (ms)')
    ax.set_ylabel('Number of Processes')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')


def _plot_algorithm_usage(ax, scheduler) -> None:
    """Plot algorithm usage statistics for adaptive scheduler."""
    ax.set_title('Algorithm Usage (Adaptive Scheduler)', fontweight='bold')
    
    usage_stats = scheduler.get_algorithm_usage_stats()
    
    if not usage_stats or all(v == 0 for v in usage_stats.values()):
        ax.text(0.5, 0.5, 'No Algorithm\nSwitching Data', 
               ha='center', va='center', fontsize=12)
        ax.axis('off')
        return
    
    # Filter out algorithms with 0% usage
    algorithms = [k for k, v in usage_stats.items() if v > 0]
    percentages = [usage_stats[k] for k in algorithms]
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(algorithms)))
    
    wedges, texts, autotexts = ax.pie(percentages, labels=algorithms, autopct='%1.1f%%',
                                        colors=colors, startangle=90)
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')


def _plot_load_balance(ax, cores) -> None:
    """Plot load balance across cores."""
    ax.set_title('Load Distribution Across Cores', fontweight='bold')
    
    core_ids = [f'Core {core.core_id}' for core in cores]
    loads = [core.get_average_load() for core in cores]
    
    bars = ax.bar(core_ids, loads, color='#1abc9c', alpha=0.7, edgecolor='black')
    
    # Add value labels
    for bar, value in zip(bars, loads):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Add average line
    avg_load = np.mean(loads)
    ax.axhline(y=avg_load, color='r', linestyle='--', alpha=0.5, 
               label=f'Average: {avg_load:.2f}')
    
    ax.set_ylabel('Average Load (ms)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')


def compare_algorithms_plot(results: Dict[str, Any]) -> None:
    """
    Create comparison plots for multiple algorithms.
    
    Args:
        results: Dictionary mapping algorithm names to their metrics
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Algorithm Comparison', fontsize=16, fontweight='bold')
    
    algorithms = list(results.keys())
    colors = plt.cm.Set2(np.linspace(0, 1, len(algorithms)))
    
    # 1. Turnaround Time
    ax = axes[0, 0]
    values = [results[algo]['metrics'].average_turnaround_time for algo in algorithms]
    ax.bar(algorithms, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_title('Average Turnaround Time')
    ax.set_ylabel('Time (ms)')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 2. Waiting Time
    ax = axes[0, 1]
    values = [results[algo]['metrics'].average_waiting_time for algo in algorithms]
    ax.bar(algorithms, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_title('Average Waiting Time')
    ax.set_ylabel('Time (ms)')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 3. Response Time
    ax = axes[0, 2]
    values = [results[algo]['metrics'].average_response_time for algo in algorithms]
    ax.bar(algorithms, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_title('Average Response Time')
    ax.set_ylabel('Time (ms)')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 4. CPU Utilization
    ax = axes[1, 0]
    values = [results[algo]['metrics'].cpu_utilization for algo in algorithms]
    ax.bar(algorithms, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_title('CPU Utilization')
    ax.set_ylabel('Percentage (%)')
    ax.set_ylim(0, 110)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 5. Throughput
    ax = axes[1, 1]
    values = [results[algo]['metrics'].throughput for algo in algorithms]
    ax.bar(algorithms, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_title('Throughput')
    ax.set_ylabel('Processes/sec')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 6. Load Balance Score
    ax = axes[1, 2]
    values = [results[algo]['metrics'].load_balance_score for algo in algorithms]
    ax.bar(algorithms, values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_title('Load Balance Score')
    ax.set_ylabel('Score (0-1)')
    ax.set_ylim(0, 1.1)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()


def plot_workload_comparison(results: Dict[str, Dict[str, Any]]) -> None:
    """
    Plot algorithm performance across different workload types.
    
    Args:
        results: Nested dict: {workload_type: {algorithm: metrics}}
    """
    workload_types = list(results.keys())
    algorithms = list(results[workload_types[0]].keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Algorithm Performance Across Workload Types', fontsize=16, fontweight='bold')
    
    metrics_to_plot = [
        ('average_turnaround_time', 'Avg Turnaround Time (ms)', axes[0, 0]),
        ('average_waiting_time', 'Avg Waiting Time (ms)', axes[0, 1]),
        ('cpu_utilization', 'CPU Utilization (%)', axes[1, 0]),
        ('throughput', 'Throughput (proc/sec)', axes[1, 1])
    ]
    
    for metric_name, title, ax in metrics_to_plot:
        x = np.arange(len(workload_types))
        width = 0.8 / len(algorithms)
        
        for i, algo in enumerate(algorithms):
            values = [getattr(results[wl][algo]['metrics'], metric_name) for wl in workload_types]
            ax.bar(x + i * width, values, width, label=algo, alpha=0.8)
        
        ax.set_title(title)
        ax.set_xticks(x + width * (len(algorithms) - 1) / 2)
        ax.set_xticklabels(workload_types)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()

