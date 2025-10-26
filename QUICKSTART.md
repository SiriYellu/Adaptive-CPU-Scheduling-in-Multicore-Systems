# Quick Start Guide

Get started with the Adaptive CPU Scheduling simulator in minutes!

## Installation

```bash
# Navigate to the project directory
cd "Adaptive CPU Scheduling in Multicore Systems"

# Install dependencies
pip install -r requirements.txt
```

## Run Your First Simulation

### Option 1: Interactive Demo (Recommended)

Run the interactive demo with a menu-driven interface:

```bash
python examples/demo.py
```

This will give you options to:
1. See the adaptive scheduler in action
2. Compare all algorithms
3. Test different workload types
4. Run all demos

### Option 2: Simple Example

Run a quick example:

```bash
python examples/simple_example.py
```

### Option 3: Algorithm Comparison

Compare all scheduling algorithms:

```bash
python examples/compare_algorithms.py
```

## Basic Usage in Your Code

### Using the Adaptive Scheduler

```python
from scheduler_simulator import MulticoreSchedulerSimulator
from algorithms.adaptive_scheduler import AdaptiveScheduler

# Create simulator with 4 cores
simulator = MulticoreSchedulerSimulator(num_cores=4)

# Use adaptive scheduler (automatically selects best algorithm)
scheduler = AdaptiveScheduler(num_cores=4)
simulator.set_scheduler(scheduler)

# Generate processes
simulator.generate_processes(
    num_processes=50,
    workload_type='mixed'  # 'cpu_bound', 'io_bound', or 'mixed'
)

# Run simulation
results = simulator.run_simulation()

# Display results
simulator.display_results()

# Show visualization (requires matplotlib)
simulator.plot_results()
```

### Using a Specific Algorithm

```python
from scheduler_simulator import MulticoreSchedulerSimulator
from algorithms.round_robin import RoundRobinScheduler

simulator = MulticoreSchedulerSimulator(num_cores=4)

# Use Round Robin with 5ms time quantum
scheduler = RoundRobinScheduler(num_cores=4, time_quantum=5.0)
simulator.set_scheduler(scheduler)

simulator.generate_processes(num_processes=30)
simulator.run_simulation()
simulator.display_results()
```

## Available Scheduling Algorithms

### Traditional Algorithms
- **FCFS** - First-Come, First-Served
- **SJF** - Shortest Job First (preemptive and non-preemptive)
- **Round Robin** - Time-sharing with configurable quantum
- **Priority** - Priority-based scheduling with aging

### Multicore Algorithms
- **Load Balancing** - Distributes work evenly across cores
- **Work Stealing** - Idle cores steal from busy cores

### Adaptive Algorithm
- **Adaptive Scheduler** - Automatically selects the best algorithm based on:
  - System load
  - Process characteristics
  - Workload type

## Understanding the Results

The simulator provides comprehensive metrics:

- **Average Turnaround Time**: Total time from process arrival to completion
- **Average Waiting Time**: Time spent waiting in the ready queue
- **Average Response Time**: Time until first execution
- **CPU Utilization**: Percentage of time CPUs are busy
- **Throughput**: Processes completed per unit time
- **Load Balance Score**: How evenly work is distributed (0-1)

## Visualization

The simulator generates multiple visualizations:

1. **Gantt Chart** - Timeline of process execution
2. **Performance Metrics** - Bar charts of key metrics
3. **Core Utilization** - Utilization per core
4. **Turnaround Times** - Distribution across processes
5. **Waiting Time Distribution** - Histogram of waiting times
6. **Algorithm Usage** - Pie chart for adaptive scheduler
7. **Load Balance** - Load distribution across cores

## Customization

### Custom Process Generation

```python
simulator.generate_processes(
    num_processes=100,        # Number of processes
    arrival_rate=5.0,         # Average inter-arrival time
    min_burst=5.0,            # Minimum burst time
    max_burst=50.0,           # Maximum burst time
    workload_type='mixed',    # Workload characteristics
    priority_range=(0, 10)    # Priority range
)
```

### Custom Processes

```python
from core.process import Process, ProcessType

# Create custom process
process = Process(
    pid=1,
    arrival_time=0.0,
    burst_time=25.0,
    priority=5,
    process_type=ProcessType.CPU_BOUND
)

simulator.add_process(process)
```

## Comparing Algorithms

```python
from examples.compare_algorithms import compare_all_algorithms

# Compare all algorithms on the same workload
results = compare_all_algorithms(
    num_cores=4,
    num_processes=50,
    workload_type='mixed'
)
```

## Tips for Best Results

1. **Use Adaptive Scheduler** for general-purpose workloads - it automatically adapts to changing conditions
2. **Use Load Balancing** for CPU-intensive workloads with long processes
3. **Use Work Stealing** for irregular workloads with variable process lengths
4. **Use SJF** when you know processes are short and want to minimize waiting time
5. **Use Round Robin** for time-sharing systems where fairness is important

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running Python 3.8+ and have installed all requirements:
```bash
pip install -r requirements.txt
```

### Visualization Not Working
Install matplotlib if plots don't show:
```bash
pip install matplotlib seaborn
```

### Performance Issues
For large simulations (>1000 processes), consider:
- Reducing the number of processes
- Increasing arrival_rate to spread processes over more time
- Disabling verbose mode: `MulticoreSchedulerSimulator(verbose=False)`

## Next Steps

- Explore the `examples/` directory for more advanced usage
- Read `README.md` for detailed documentation
- Modify algorithms in `algorithms/` to experiment with custom scheduling policies
- Create custom visualizations using the metrics data

## Quick Reference

```python
# Import main components
from scheduler_simulator import MulticoreSchedulerSimulator
from algorithms.adaptive_scheduler import AdaptiveScheduler

# Create and configure
sim = MulticoreSchedulerSimulator(num_cores=4)
sim.set_scheduler(AdaptiveScheduler(num_cores=4))
sim.generate_processes(num_processes=50)

# Run and visualize
sim.run_simulation()
sim.display_results()
sim.plot_results()
```

Happy scheduling! 🚀

