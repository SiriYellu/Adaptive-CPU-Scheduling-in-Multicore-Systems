# Adaptive CPU Scheduling in Multicore Systems

A comprehensive simulation framework for studying and comparing various CPU scheduling algorithms in multicore systems, with adaptive scheduling capabilities that dynamically adjust based on system state and workload characteristics.

## Features

### Scheduling Algorithms Implemented

#### Traditional Algorithms
- **FCFS (First-Come, First-Served)**: Simplest scheduling algorithm that processes tasks in order of arrival
- **SJF (Shortest Job First)**: Prioritizes processes with shortest burst time
- **Round Robin**: Time-sharing algorithm with configurable time quantum
- **Priority Scheduling**: Schedules based on process priority levels

#### Multicore-Specific Algorithms
- **Load Balancing**: Distributes processes evenly across cores to minimize load imbalance
- **Work Stealing**: Idle cores steal work from busy cores to improve utilization
- **Affinity-Based**: Considers CPU affinity to reduce cache misses

#### Adaptive Scheduling
- **Dynamic Algorithm Selection**: Automatically selects the best scheduling algorithm based on:
  - System load (high/medium/low)
  - Process characteristics (I/O-bound vs CPU-bound)
  - Number of active cores
  - Historical performance metrics
- **Self-tuning Parameters**: Automatically adjusts time quantum and other parameters

### Simulation Features
- Multi-core CPU simulation (configurable number of cores)
- Process generation with realistic attributes (burst time, priority, I/O behavior)
- Real-time performance metrics tracking
- Beautiful visualization of CPU utilization and scheduling behavior

### Performance Metrics
- **Average Turnaround Time**: Total time from arrival to completion
- **Average Waiting Time**: Time spent in ready queue
- **Average Response Time**: Time from arrival to first execution
- **CPU Utilization**: Percentage of time CPUs are busy
- **Throughput**: Number of processes completed per unit time
- **Load Balance**: Distribution of work across cores

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd "Adaptive CPU Scheduling in Multicore Systems"

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Simulation

```python
from scheduler_simulator import MulticoreSchedulerSimulator
from algorithms.adaptive_scheduler import AdaptiveScheduler

# Create simulator with 4 cores
simulator = MulticoreSchedulerSimulator(num_cores=4)

# Use adaptive scheduling
scheduler = AdaptiveScheduler(num_cores=4)
simulator.set_scheduler(scheduler)

# Generate and run simulation
simulator.generate_processes(num_processes=50)
results = simulator.run_simulation()

# Display results
simulator.display_results()
simulator.plot_results()
```

### Compare Algorithms

```python
from examples.compare_algorithms import compare_all_algorithms

# Compare all algorithms on the same workload
results = compare_all_algorithms(
    num_cores=4,
    num_processes=100,
    workload_type='mixed'  # 'cpu_bound', 'io_bound', or 'mixed'
)
```

### Run Demo

```python
# Run the interactive demo
python examples/demo.py
```

## Project Structure

```
.
├── algorithms/
│   ├── base_scheduler.py           # Abstract base class for schedulers
│   ├── fcfs.py                      # First-Come, First-Served
│   ├── sjf.py                       # Shortest Job First
│   ├── round_robin.py               # Round Robin
│   ├── priority.py                  # Priority Scheduling
│   ├── load_balancing.py            # Load Balancing for multicore
│   ├── work_stealing.py             # Work Stealing
│   └── adaptive_scheduler.py        # Adaptive Scheduling (main feature)
├── core/
│   ├── process.py                   # Process class
│   ├── cpu.py                       # CPU core simulation
│   └── metrics.py                   # Performance metrics tracking
├── scheduler_simulator.py           # Main simulator
├── visualization/
│   └── plots.py                     # Visualization utilities
├── examples/
│   ├── demo.py                      # Interactive demo
│   └── compare_algorithms.py       # Algorithm comparison
├── requirements.txt
└── README.md
```

## How Adaptive Scheduling Works

The adaptive scheduler monitors the system state and automatically selects the most appropriate scheduling algorithm:

1. **High Load, CPU-bound processes**: Uses Load Balancing to distribute work evenly
2. **Low Load, mixed processes**: Uses Work Stealing for better core utilization
3. **Balanced Load, short processes**: Uses SJF to minimize waiting time
4. **High I/O activity**: Uses Priority scheduling with I/O-bound processes prioritized

The scheduler continuously evaluates performance and can switch algorithms during runtime if conditions change.

## Example Output

```
=== Adaptive CPU Scheduling Simulation ===
Cores: 4
Processes: 100
Algorithm: Adaptive (Dynamic)

Performance Metrics:
  Average Turnaround Time: 45.2ms
  Average Waiting Time: 12.3ms
  Average Response Time: 3.1ms
  CPU Utilization: 87.5%
  Throughput: 22.1 processes/sec
  Load Balance Score: 0.92
  
Algorithm Usage:
  Load Balancing: 45%
  Work Stealing: 30%
  SJF: 15%
  Priority: 10%
```

## Requirements

- Python 3.8+
- NumPy
- Matplotlib
- Pandas (for data analysis)

## Future Enhancements

- Real-time system integration
- Machine learning-based prediction
- GPU scheduling support
- Power-aware scheduling
- NUMA-aware scheduling

## License

MIT License

## Author

Built as a research project for studying adaptive scheduling in multicore systems.

