# Installation Guide

## System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- 50 MB of disk space

## Supported Platforms

- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, Debian, Fedora, etc.)

## Installation Steps

### 1. Verify Python Installation

```bash
python --version
```

You should see Python 3.8 or higher. If not, download from [python.org](https://www.python.org/downloads/).

### 2. Navigate to Project Directory

```bash
cd "Adaptive CPU Scheduling in Multicore Systems"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- numpy (numerical computing)
- matplotlib (visualization)
- pandas (data analysis)
- seaborn (statistical visualization)
- colorama (colored terminal output)
- tabulate (table formatting)

### 4. Verify Installation

```bash
python test_installation.py
```

You should see:
```
*** All tests passed! Installation successful! ***
```

## Troubleshooting

### Problem: Python not found

**Solution**: Make sure Python is installed and added to your PATH.

```bash
# Windows
python --version

# macOS/Linux
python3 --version
```

### Problem: pip not found

**Solution**: Install pip:

```bash
# Windows
python -m ensurepip --upgrade

# macOS/Linux
python3 -m ensurepip --upgrade
```

### Problem: Permission denied

**Solution**: Use `--user` flag:

```bash
pip install --user -r requirements.txt
```

### Problem: Module not found during execution

**Solution**: Ensure you're running from the project directory:

```bash
cd "Adaptive CPU Scheduling in Multicore Systems"
python test_installation.py
```

### Problem: Visualization not working

**Solution**: Make sure matplotlib is installed:

```bash
pip install matplotlib seaborn
```

For Linux, you may need additional dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Problem: Import errors with relative imports

**Solution**: Make sure you're running scripts from the project root directory, not from subdirectories.

## Alternative Installation (Virtual Environment)

It's recommended to use a virtual environment:

### Windows

```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Verifying Components

After installation, verify each component:

### 1. Core Modules

```python
from core import Process, CPUCore, MetricsCollector
print("Core modules OK")
```

### 2. Algorithms

```python
from algorithms import (
    FCFSScheduler,
    SJFScheduler,
    RoundRobinScheduler,
    PriorityScheduler,
    LoadBalancingScheduler,
    WorkStealingScheduler,
    AdaptiveScheduler
)
print("All algorithms OK")
```

### 3. Simulator

```python
from scheduler_simulator import MulticoreSchedulerSimulator
print("Simulator OK")
```

### 4. Visualization

```python
from visualization.plots import plot_simulation_results
print("Visualization OK")
```

## Updating Dependencies

To update all dependencies to the latest versions:

```bash
pip install --upgrade -r requirements.txt
```

## Uninstallation

To remove the project and its dependencies:

```bash
# If using virtual environment
deactivate
cd ..
rm -rf "Adaptive CPU Scheduling in Multicore Systems"

# If installed globally, uninstall dependencies
pip uninstall -r requirements.txt -y
```

## Development Installation

For development, you may want additional tools:

```bash
pip install pytest pytest-cov black flake8 mypy
```

## Docker Installation (Optional)

If you prefer Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "test_installation.py"]
```

Build and run:

```bash
docker build -t adaptive-scheduler .
docker run -it adaptive-scheduler python examples/demo.py
```

## Quick Start After Installation

Once installed, run:

```bash
# Test installation
python test_installation.py

# Run simple example
python examples/simple_example.py

# Run interactive demo
python examples/demo.py

# Compare algorithms
python examples/compare_algorithms.py
```

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review error messages carefully
3. Ensure you're using Python 3.8+
4. Verify all dependencies are installed
5. Try running from a fresh virtual environment

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt
- Paths use backslashes: `\`
- May need to use `python` instead of `python3`

### macOS

- May need to use `python3` explicitly
- Install via Homebrew: `brew install python3`
- XCode Command Line Tools may be required

### Linux

- May need to use `python3` explicitly
- Install via package manager: `apt`, `yum`, `dnf`
- May require `python3-dev` package

## Next Steps

After successful installation:

1. Read `QUICKSTART.md` for usage examples
2. Run `python examples/demo.py` for an interactive demo
3. Explore `README.md` for comprehensive documentation
4. Check `PROJECT_OVERVIEW.md` for project details

## Support

For issues or questions:
- Check documentation files
- Review example scripts
- Verify Python version and dependencies

---

**Installation complete! You're ready to explore adaptive CPU scheduling!** 🚀

