"""
Performance metrics tracking for scheduling algorithms.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
import statistics


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    average_turnaround_time: float
    average_waiting_time: float
    average_response_time: float
    cpu_utilization: float
    throughput: float
    total_context_switches: int
    load_balance_score: float
    algorithm_name: str
    num_cores: int
    num_processes: int
    total_simulation_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'Average Turnaround Time': f"{self.average_turnaround_time:.2f}ms",
            'Average Waiting Time': f"{self.average_waiting_time:.2f}ms",
            'Average Response Time': f"{self.average_response_time:.2f}ms",
            'CPU Utilization': f"{self.cpu_utilization:.2f}%",
            'Throughput': f"{self.throughput:.2f} processes/sec",
            'Context Switches': self.total_context_switches,
            'Load Balance Score': f"{self.load_balance_score:.2f}",
            'Algorithm': self.algorithm_name,
            'Cores': self.num_cores,
            'Processes': self.num_processes,
            'Simulation Time': f"{self.total_simulation_time:.2f}ms"
        }
    
    def __repr__(self) -> str:
        return (f"\nPerformance Metrics ({self.algorithm_name}):\n"
                f"  Avg Turnaround Time: {self.average_turnaround_time:.2f}ms\n"
                f"  Avg Waiting Time: {self.average_waiting_time:.2f}ms\n"
                f"  Avg Response Time: {self.average_response_time:.2f}ms\n"
                f"  CPU Utilization: {self.cpu_utilization:.2f}%\n"
                f"  Throughput: {self.throughput:.2f} processes/sec\n"
                f"  Context Switches: {self.total_context_switches}\n"
                f"  Load Balance Score: {self.load_balance_score:.2f}")


class MetricsCollector:
    """Collects and calculates performance metrics from simulation results."""
    
    @staticmethod
    def calculate_metrics(
        processes: List,
        cores: List,
        total_time: float,
        algorithm_name: str,
        context_switches: int = 0
    ) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            processes: List of completed processes
            cores: List of CPU cores
            total_time: Total simulation time
            algorithm_name: Name of the scheduling algorithm
            context_switches: Total number of context switches
            
        Returns:
            PerformanceMetrics object with calculated metrics
        """
        completed_processes = [p for p in processes if p.is_completed()]
        
        if not completed_processes:
            return PerformanceMetrics(
                average_turnaround_time=0.0,
                average_waiting_time=0.0,
                average_response_time=0.0,
                cpu_utilization=0.0,
                throughput=0.0,
                total_context_switches=context_switches,
                load_balance_score=0.0,
                algorithm_name=algorithm_name,
                num_cores=len(cores),
                num_processes=len(processes),
                total_simulation_time=total_time
            )
        
        # Calculate time-based metrics
        avg_turnaround = sum(p.turnaround_time for p in completed_processes) / len(completed_processes)
        avg_waiting = sum(p.waiting_time for p in completed_processes) / len(completed_processes)
        avg_response = sum(p.response_time for p in completed_processes) / len(completed_processes)
        
        # Calculate CPU utilization
        total_busy_time = sum(core.total_busy_time for core in cores)
        total_possible_time = total_time * len(cores)
        cpu_utilization = (total_busy_time / total_possible_time * 100) if total_possible_time > 0 else 0.0
        
        # Calculate throughput
        throughput = (len(completed_processes) / total_time * 1000) if total_time > 0 else 0.0
        
        # Calculate load balance score (lower standard deviation = better balance)
        core_utilizations = [core.get_utilization(total_time) for core in cores]
        if len(core_utilizations) > 1:
            std_dev = statistics.stdev(core_utilizations)
            # Normalize to 0-1 scale (0 = worst, 1 = best)
            load_balance_score = max(0.0, 1.0 - (std_dev / 100.0))
        else:
            load_balance_score = 1.0
        
        # Sum context switches from processes
        total_context_switches = sum(p.context_switches for p in completed_processes) + context_switches
        
        return PerformanceMetrics(
            average_turnaround_time=avg_turnaround,
            average_waiting_time=avg_waiting,
            average_response_time=avg_response,
            cpu_utilization=cpu_utilization,
            throughput=throughput,
            total_context_switches=total_context_switches,
            load_balance_score=load_balance_score,
            algorithm_name=algorithm_name,
            num_cores=len(cores),
            num_processes=len(processes),
            total_simulation_time=total_time
        )
    
    @staticmethod
    def compare_metrics(metrics_list: List[PerformanceMetrics]) -> Dict[str, Any]:
        """
        Compare multiple metrics and identify best performers.
        
        Args:
            metrics_list: List of PerformanceMetrics to compare
            
        Returns:
            Dictionary with comparison results
        """
        if not metrics_list:
            return {}
        
        comparison = {
            'best_turnaround': min(metrics_list, key=lambda m: m.average_turnaround_time),
            'best_waiting': min(metrics_list, key=lambda m: m.average_waiting_time),
            'best_response': min(metrics_list, key=lambda m: m.average_response_time),
            'best_utilization': max(metrics_list, key=lambda m: m.cpu_utilization),
            'best_throughput': max(metrics_list, key=lambda m: m.throughput),
            'best_load_balance': max(metrics_list, key=lambda m: m.load_balance_score),
            'fewest_context_switches': min(metrics_list, key=lambda m: m.total_context_switches)
        }
        
        return comparison

