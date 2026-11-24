# OSSim – OS Resource Management Simulator

**Student / Repository Maintainer:** Kumar Subodh  
**Roll Number:** 2401010205  
**Course:** Operating Systems Lab (ENCS351)  
**Technology:** Python 3 and Bash

## Overview

OSSim is a single, menu-driven application that demonstrates core operating-system resource-management functions. It brings CPU scheduling, memory allocation, deadlock safety, disk scheduling, performance comparison, CSV reporting, and activity logging into one integrated project.

This repository is an adapted and maintained version of the upstream [OS-LAB-CAPTSONE-PROJECT](https://github.com/monishkabajaj/OS-LAB-CAPTSONE-PROJECT-). The upstream repository is linked here for source transparency; this version's project identification and documentation are maintained for the student listed above.

## Features

| Module | Algorithms / features |
|---|---|
| CPU scheduling | FCFS, non-preemptive SJF, Round Robin |
| Memory management | First Fit, Best Fit, Worst Fit |
| Deadlock management | Banker's safety algorithm |
| Disk scheduling | FCFS, SSTF, SCAN |
| Performance analysis | Average waiting and turnaround time comparison |
| Reporting | CSV reports and timestamped activity log |
| Bash integration | Run and cleanup scripts |

## Requirements

- Python 3.9 or later
- Windows: Python installed and available in PowerShell / VS Code terminal
- Bash integration on Windows: Git Bash or WSL
- Linux and macOS: Python 3 and Bash

The core application uses only Python's standard library. No third-party package installation is required.

## Run

Open a terminal in the project root (the directory containing `main.py`).

### Windows PowerShell / VS Code terminal

```powershell
python main.py
```

### Linux / macOS / Git Bash / WSL

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

## Main menu

1. **CPU Scheduling** – select FCFS, SJF, or Round Robin.
2. **Memory Management** – select First Fit, Best Fit, or Worst Fit.
3. **Deadlock Detection** – check a resource allocation state using Banker's algorithm.
4. **Disk Scheduling** – select FCFS, SSTF, or SCAN.
5. **Performance Comparison** – compare CPU algorithms using the same sample workload.
6. **Activity Log** – display recent actions.
0. **Exit** – close OSSim.

## Sample process dataset

The file `data/sample_processes.csv` contains:

| PID | Arrival time | Burst time |
|---|---:|---:|
| P1 | 0 | 7 |
| P2 | 2 | 4 |
| P3 | 4 | 1 |
| P4 | 5 | 4 |

The CPU menu also provides this built-in sample. Memory, deadlock, and disk modules include their own documented demonstration datasets.

## Output files

OSSim creates these directories automatically when it runs:

- `reports/` – CSV files containing scheduling, memory, disk, and comparison results.
- `logs/` – `activity.log`, which records application activity with timestamps.

Generated output is intentionally excluded from Git using `.gitignore`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The test suite covers normal algorithm results, invalid inputs, allocation failure, Banker's safety validation, and disk-boundary / SCAN cases.

## Bash scripts

- `scripts/run.sh` – locates the project root and launches the Python application.
- `scripts/cleanup.sh` – removes generated CSV reports and the activity log without deleting source files.

## Algorithms and assumptions

- CPU scheduling uses integer time units. SJF is non-preemptive.
- Round Robin uses a positive time quantum. Newly arrived processes are added to the ready queue before the pre-empted process is requeued.
- Memory uses variable-sized available blocks. Each request is assigned to at most one block.
- Banker's algorithm calculates `Need = Maximum − Allocation` and searches for a safe completion sequence.
- Disk tracks range from 0 to 199 by default. SCAN initially moves toward higher-numbered tracks, reaches the upper boundary when it must reverse to service lower requests, and then moves downward.
- OSSim is an educational simulator; it does not control real processes, physical RAM, or storage hardware.

## Limitations and future enhancements

The simulator uses deterministic teaching datasets. Possible extensions include preemptive SJF, priority scheduling, paging and page replacement, interactive resource requests, LOOK / C-LOOK, configurable CSV input for every module, and graphical performance charts.

## Troubleshooting

- If `python` is not recognized on Windows, install Python and enable **Add Python to PATH**, or try `py main.py`.
- If Bash reports permission denied, run `chmod +x scripts/run.sh`.
- If imports fail, make sure the terminal is in the project root.
