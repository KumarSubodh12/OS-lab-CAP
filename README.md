# OSLab CAP

### Interactive Operating Systems Laboratory

**Project author and maintainer:** Kumar Subodh · **Roll number:** 2401010205
**Course:** Operating Systems Lab · ENCS351

OSLab CAP is a standalone, full-stack learning website for exploring operating-systems algorithms. It combines a responsive browser interface with a Python API that validates simulator inputs and calculates results. This repository contains the application source and its deployment configuration.

## Live website

**Deployment:** [https://os-lab-cap.onrender.com](https://os-lab-cap.onrender.com) · **Simulators:** [open OSLab CAP](https://os-lab-cap.onrender.com)

The hosted version runs in public-demo mode. The monitor that reads the server's actual CPU, memory, and processes is available only when the app is run locally.

## Simulators

| Topic | What you can explore |
|---|---|
| CPU scheduling | FCFS, non-preemptive SJF, Round Robin, and Priority; Gantt timeline, waiting time, turnaround time |
| Memory management | First Fit, Best Fit, Worst Fit, paging, segmentation, and fragmentation |
| Deadlock | Banker’s safety check, remaining needs, and safe sequence |
| Mini shell | `help`, `pwd`, `ls`, `cd`, `mkdir`, `touch`, `write`, `cat`, `rm`, and `clear` in an isolated virtual file space |
| Disk scheduling | FCFS, SSTF, SCAN, C-SCAN, and LOOK; head path and seek distance |
| Page replacement | FIFO, LRU, and Optimal; step-by-step frames, hits, and faults |
| Resource monitor | Read-only CPU, RAM, and process snapshot on the local host |
| Virtual file system | Create, rename, search, and delete browser-local virtual files |
| Synchronization | Producer–Consumer, Readers–Writers, and Dining Philosophers scenarios |
| Address translation | Page-table lookup, TLB hits/misses, and page faults |

All simulator inputs can be changed. The shell never launches operating-system commands and never accesses real files. The virtual file system stays in browser storage.

## Run locally

Python 3.13 is recommended. From the repository folder:

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

To use the live resource monitor, run locally with `psutil` installed (it is included in `requirements.txt`).

## Deploy on Render

This repository includes `render.yaml`. In Render, create a new **Blueprint** and connect the `KumarSubodh12/OS-lab-CAP` GitHub repository. Render reads the build/start commands and enables `OSLAB_DEMO=1` for the public service. Pushes to `main` can then trigger deployments from this repository.

## Project structure

```text
app.py                 Flask pages and JSON simulation API
templates/index.html   Main application interface
static/css/style.css   Responsive visual design
static/js/app.js       Simulator controls and result views
render.yaml            Render deployment configuration
requirements.txt       Python runtime dependencies
```

## Ownership and implementation

OSLab CAP is Kumar Subodh’s course project (Roll No. 2401010205). The current application in this repository is a standalone implementation of standard operating-systems concepts; it does not import application code from another project. The algorithms themselves are established topics taught in operating-systems courses.
