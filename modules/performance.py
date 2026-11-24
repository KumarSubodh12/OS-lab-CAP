"""Compare CPU scheduling algorithms on one common workload."""

from modules.cpu_scheduling import SAMPLE, fcfs, sjf_non_preemptive, round_robin
from modules.reporting import save_csv, log_event


def run_comparison():
    algorithms = [
        ("FCFS", lambda: fcfs(SAMPLE)),
        ("SJF", lambda: sjf_non_preemptive(SAMPLE)),
        ("Round Robin (q=2)", lambda: round_robin(SAMPLE, 2)),
    ]
    rows = []

    print("\nCPU algorithm comparison (same sample dataset)")
    print(f"{'Algorithm':<20}{'Avg waiting':>15}{'Avg turnaround':>18}")

    for name, run_algorithm in algorithms:
        metrics, _ = run_algorithm()
        average_waiting = sum(item["waiting"] for item in metrics) / len(metrics)
        average_turnaround = sum(item["turnaround"] for item in metrics) / len(metrics)
        rows.append([name, round(average_waiting, 2), round(average_turnaround, 2)])
        print(f"{name:<20}{average_waiting:>15.2f}{average_turnaround:>18.2f}")

    save_csv(
        "cpu_algorithm_comparison.csv",
        ["Algorithm", "Average waiting time", "Average turnaround time"],
        rows,
    )
    print("\nObservation: lower averages are better for this dataset; no algorithm is best for every workload.")
    log_event("CPU algorithm comparison completed")
