"""CPU scheduling algorithms and interactive demonstration menu."""

from modules.reporting import save_csv, log_event

SAMPLE = [
    {"pid": "P1", "arrival": 0, "burst": 7},
    {"pid": "P2", "arrival": 2, "burst": 4},
    {"pid": "P3", "arrival": 4, "burst": 1},
    {"pid": "P4", "arrival": 5, "burst": 4},
]


def validate_processes(processes):
    if not processes:
        raise ValueError("At least one process is required.")

    seen = set()
    for process in processes:
        if not isinstance(process, dict) or not {"pid", "arrival", "burst"} <= process.keys():
            raise ValueError("Each process must contain pid, arrival, and burst fields.")

        pid = str(process["pid"]).strip()
        arrival = int(process["arrival"])
        burst = int(process["burst"])

        if not pid or pid in seen:
            raise ValueError("Process IDs must be non-empty and unique.")
        if arrival < 0 or burst <= 0:
            raise ValueError("Arrival time must be >= 0 and burst time must be > 0.")
        seen.add(pid)


def calculate_metrics(rows):
    result = []
    for process in rows:
        turnaround = process["completion"] - process["arrival"]
        waiting = turnaround - process["burst"]
        response = process["first_start"] - process["arrival"]
        result.append({
            "pid": process["pid"],
            "arrival": process["arrival"],
            "burst": process["burst"],
            "completion": process["completion"],
            "turnaround": turnaround,
            "waiting": waiting,
            "response": response,
        })
    return result


def fcfs(processes):
    validate_processes(processes)
    clock, schedule, completed = 0, [], []

    for process in sorted(processes, key=lambda item: (int(item["arrival"]), str(item["pid"]))):
        arrival = int(process["arrival"])
        burst = int(process["burst"])
        start = max(clock, arrival)
        end = start + burst

        schedule.append((process["pid"], start, end))
        completed.append({
            **process,
            "arrival": arrival,
            "burst": burst,
            "first_start": start,
            "completion": end,
        })
        clock = end

    return calculate_metrics(completed), schedule


def sjf_non_preemptive(processes):
    validate_processes(processes)
    pending = [
        dict(process, arrival=int(process["arrival"]), burst=int(process["burst"]))
        for process in processes
    ]
    clock, completed, schedule = 0, [], []

    while pending:
        ready = [process for process in pending if process["arrival"] <= clock]
        if not ready:
            clock = min(process["arrival"] for process in pending)
            ready = [process for process in pending if process["arrival"] <= clock]

        process = min(
            ready,
            key=lambda item: (item["burst"], item["arrival"], str(item["pid"]))
        )
        pending.remove(process)

        start, end = clock, clock + process["burst"]
        schedule.append((process["pid"], start, end))
        completed.append({**process, "first_start": start, "completion": end})
        clock = end

    return calculate_metrics(completed), schedule


def round_robin(processes, quantum=2):
    validate_processes(processes)
    quantum = int(quantum)
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero.")

    pending = sorted(
        [
            dict(process, arrival=int(process["arrival"]), burst=int(process["burst"]))
            for process in processes
        ],
        key=lambda item: (item["arrival"], str(item["pid"])),
    )
    remaining = {process["pid"]: process["burst"] for process in pending}
    first_start, completion, schedule = {}, {}, []
    ready, next_process, clock = [], 0, 0

    while next_process < len(pending) or ready:
        if not ready and next_process < len(pending):
            clock = max(clock, pending[next_process]["arrival"])

        while next_process < len(pending) and pending[next_process]["arrival"] <= clock:
            ready.append(pending[next_process])
            next_process += 1

        process = ready.pop(0)
        pid = process["pid"]
        first_start.setdefault(pid, clock)

        run_time = min(quantum, remaining[pid])
        start, end = clock, clock + run_time
        schedule.append((pid, start, end))
        clock = end
        remaining[pid] -= run_time

        # Arrivals during this time slice join before the pre-empted process.
        while next_process < len(pending) and pending[next_process]["arrival"] <= clock:
            ready.append(pending[next_process])
            next_process += 1

        if remaining[pid] > 0:
            ready.append(process)
        else:
            completion[pid] = clock

    completed = [
        {
            **process,
            "first_start": first_start[process["pid"]],
            "completion": completion[process["pid"]],
        }
        for process in pending
    ]
    return calculate_metrics(completed), schedule


def print_result(name, metrics, schedule):
    print(f"\n{name} results")
    print("Gantt trace:", " | ".join(
        f"{pid}[{start}-{end}]" for pid, start, end in schedule
    ))
    print(f"{'PID':<6}{'CT':>6}{'TAT':>7}{'WT':>7}{'RT':>7}")

    for result in sorted(metrics, key=lambda item: str(item["pid"])):
        print(
            f"{result['pid']:<6}{result['completion']:>6}"
            f"{result['turnaround']:>7}{result['waiting']:>7}"
            f"{result['response']:>7}"
        )

    average_waiting = sum(item["waiting"] for item in metrics) / len(metrics)
    average_turnaround = sum(item["turnaround"] for item in metrics) / len(metrics)
    print(f"Average waiting time: {average_waiting:.2f}")
    print(f"Average turnaround time: {average_turnaround:.2f}")

    save_csv(
        f"{name.lower().replace(' ', '_')}_results.csv",
        ["PID", "Arrival", "Burst", "Completion", "Turnaround", "Waiting", "Response"],
        [[
            item["pid"], item["arrival"], item["burst"], item["completion"],
            item["turnaround"], item["waiting"], item["response"],
        ] for item in metrics],
    )
    log_event(f"CPU scheduling executed: {name}")


def run_cpu_menu():
    choice = input("Use sample processes? (y/n): ").strip().lower()

    if choice == "y":
        processes = SAMPLE
    elif choice == "n":
        count = int(input("Number of processes: "))
        if count <= 0:
            raise ValueError("Number of processes must be positive.")

        processes = []
        for index in range(count):
            print(f"Process {index + 1}")
            processes.append({
                "pid": input("PID: ").strip(),
                "arrival": int(input("Arrival time: ")),
                "burst": int(input("Burst time: ")),
            })
    else:
        raise ValueError("Enter y or n.")

    print("1. FCFS  2. SJF (non-preemptive)  3. Round Robin")
    algorithm = input("Algorithm: ").strip()

    if algorithm == "1":
        name, result = "FCFS", fcfs(processes)
    elif algorithm == "2":
        name, result = "SJF", sjf_non_preemptive(processes)
    elif algorithm == "3":
        quantum = int(input("Time quantum: "))
        name, result = "Round Robin", round_robin(processes, quantum)
    else:
        raise ValueError("Unknown scheduling algorithm.")

    print_result(name, *result)
