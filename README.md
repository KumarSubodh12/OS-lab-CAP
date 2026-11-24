# OSSim – OS Resource Management Simulator

**Student / Repository Maintainer:** Kumar Subodh  
**Roll Number:** 2401010205  
**Course:** Operating Systems Lab (ENCS351)  
**Language and integration:** Python 3 + Bash

## Project Overview

OSSim is an integrated, menu-driven Python and Bash application that simulates core operating-system resource-management functions. It includes CPU scheduling, memory allocation, deadlock safety analysis, disk scheduling, algorithm comparison, CSV reporting, and activity logging.

## Modules and Algorithms

| Module | Implemented algorithms / functions |
|---|---|
| CPU scheduling | FCFS, non-preemptive SJF, Round Robin |
| Memory management | First Fit, Best Fit, Worst Fit |
| Deadlock management | Banker's safety algorithm |
| Disk scheduling | FCFS, SSTF, SCAN |
| Performance analysis | Average waiting time and turnaround time comparison |
| Reporting | CSV exports and timestamped activity log |

## Requirements

- Python 3.9 or later
- Windows: Python installed; run using PowerShell or the VS Code terminal
- Bash integration: Git Bash or WSL on Windows; Bash is available by default on most Linux/macOS systems
- Core simulation uses the Python standard library. `requirements.txt` lists the optional plotting dependency used for future chart extensions.

## Run the Application

### Windows (PowerShell / VS Code terminal)

From the project root (the folder containing `main.py`):

```powershell
python main.py
```

### Linux / macOS / Git Bash / WSL

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

## Main Menu

1. **CPU Scheduling** – run FCFS, non-preemptive SJF, or Round Robin.
2. **Memory Management** – run First Fit, Best Fit, or Worst Fit.
3. **Deadlock Detection** – evaluate a resource state using Banker's safety algorithm.
4. **Disk Scheduling** – run FCFS, SSTF, or SCAN.
5. **Performance Comparison** – compare CPU algorithms using a common sample workload.
6. **Activity Log** – view recent application events.
0. **Exit** – close the application.

## Sample Input

The file `data/sample_processes.csv` contains the sample CPU process workload:

| PID | Arrival time | Burst time |
|---|---:|---:|
| P1 | 0 | 7 |
| P2 | 2 | 4 |
| P3 | 4 | 1 |
| P4 | 5 | 4 |

The memory, deadlock, and disk modules also include built-in teaching datasets for quick demonstrations.

## Generated Output

The application automatically creates these folders when needed:

- `reports/` – CSV reports for CPU scheduling, memory allocation, disk scheduling, and algorithm comparisons.
- `logs/` – `activity.log`, containing timestamped application activity.

Generated output is intentionally excluded from version control by `.gitignore`.

## Run the Tests

```bash
python -m unittest discover -s tests -v
```

The test suite checks scheduling results, invalid burst-time handling, memory allocation, Banker's safety detection, and disk request boundaries.

## Bash Scripts

- `scripts/run.sh` – launches the Python application from the project root.
- `scripts/cleanup.sh` – removes generated CSV reports and the activity log while preserving source files.

## Design Notes and Assumptions

- CPU scheduling uses integer time units. SJF is non-preemptive.
- Round Robin uses a user-supplied positive time quantum.
- Memory blocks are represented as variable-sized free regions. Each request is allocated once and the unused capacity remains available in that block.
- Banker's algorithm calculates `Need = Maximum − Allocation` and checks whether a safe process-completion sequence exists.
- Disk tracks are numbered from 0 through 199. SCAN first moves toward higher-numbered tracks and then reverses direction.
- OSSim is an educational simulator. It does not control real operating-system processes, physical RAM, or storage devices.

## Troubleshooting

- If `python` is not recognized on Windows, install Python and enable **Add Python to PATH**, or try `py main.py`.
- If Bash reports permission denied, run `chmod +x scripts/run.sh`.
- If a module import fails, run the command from the project root (the folder containing `main.py`).


