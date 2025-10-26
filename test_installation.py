"""
Quick test script to verify the installation and basic functionality.
"""
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from core import Process, CPUCore, MetricsCollector
        from algorithms import (
            FCFSScheduler, SJFScheduler, RoundRobinScheduler,
            PriorityScheduler, LoadBalancingScheduler,
            WorkStealingScheduler, AdaptiveScheduler
        )
        from scheduler_simulator import MulticoreSchedulerSimulator
        print("[PASS] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_basic_simulation():
    """Test a basic simulation run."""
    print("\nTesting basic simulation...")
    try:
        from scheduler_simulator import MulticoreSchedulerSimulator
        from algorithms.adaptive_scheduler import AdaptiveScheduler
        
        # Create simulator
        simulator = MulticoreSchedulerSimulator(num_cores=2, verbose=False)
        
        # Set scheduler
        scheduler = AdaptiveScheduler(num_cores=2)
        simulator.set_scheduler(scheduler)
        
        # Generate processes
        simulator.generate_processes(num_processes=10)
        
        # Run simulation
        metrics = simulator.run_simulation()
        
        # Check results
        assert metrics is not None
        assert metrics.average_turnaround_time > 0
        assert metrics.cpu_utilization > 0
        assert len(simulator.completed_processes) == 10
        
        print("[PASS] Basic simulation successful")
        print(f"  - Completed {len(simulator.completed_processes)} processes")
        print(f"  - Average turnaround time: {metrics.average_turnaround_time:.2f}ms")
        print(f"  - CPU utilization: {metrics.cpu_utilization:.2f}%")
        return True
    except Exception as e:
        print(f"[FAIL] Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_algorithms():
    """Test that all algorithms can run."""
    print("\nTesting all algorithms...")
    try:
        from scheduler_simulator import MulticoreSchedulerSimulator
        from algorithms import (
            FCFSScheduler, SJFScheduler, RoundRobinScheduler,
            PriorityScheduler, LoadBalancingScheduler,
            WorkStealingScheduler, AdaptiveScheduler
        )
        
        algorithms = [
            ('FCFS', FCFSScheduler(2)),
            ('SJF', SJFScheduler(2)),
            ('Round Robin', RoundRobinScheduler(2)),
            ('Priority', PriorityScheduler(2)),
            ('Load Balancing', LoadBalancingScheduler(2)),
            ('Work Stealing', WorkStealingScheduler(2)),
            ('Adaptive', AdaptiveScheduler(2))
        ]
        
        for name, scheduler in algorithms:
            simulator = MulticoreSchedulerSimulator(num_cores=2, verbose=False)
            simulator.set_scheduler(scheduler)
            simulator.generate_processes(num_processes=5)
            metrics = simulator.run_simulation()
            assert metrics is not None
            print(f"  [PASS] {name} scheduler works")
        
        print("[PASS] All algorithms tested successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Algorithm test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test if visualization dependencies are available."""
    print("\nTesting visualization dependencies...")
    try:
        import matplotlib
        import seaborn
        print("[PASS] Visualization dependencies available")
        return True
    except ImportError as e:
        print(f"[WARN] Visualization dependencies not available: {e}")
        print("  Install with: pip install matplotlib seaborn")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Adaptive CPU Scheduling - Installation Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Basic Simulation", test_basic_simulation()))
    results.append(("All Algorithms", test_all_algorithms()))
    results.append(("Visualization", test_visualization()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:<25} {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n*** All tests passed! Installation successful! ***")
        print("\nNext steps:")
        print("  1. Run: python examples/simple_example.py")
        print("  2. Run: python examples/demo.py")
        print("  3. Read: QUICKSTART.md")
        return 0
    elif passed_count >= total_count - 1:
        print("\n[INFO] Core functionality working!")
        print("[WARN] Some optional features may not be available.")
        return 0
    else:
        print("\n[ERROR] Installation has issues. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

