"""Disk-head scheduling algorithms."""

from modules.reporting import save_csv, log_event


def disk_schedule(requests, head, algorithm, disk_size=200):
    disk_size = int(disk_size)
    head = int(head)
    requests = [int(request) for request in requests]

    if disk_size <= 0:
        raise ValueError("Disk size must be greater than zero.")
    if not requests:
        raise ValueError("At least one disk request is required.")
    if any(request < 0 or request >= disk_size for request in requests):
        raise ValueError(f"Requests must be between 0 and {disk_size - 1}.")
    if not 0 <= head < disk_size:
        raise ValueError("Initial head position is outside the disk.")

    algorithm = algorithm.upper()
    if algorithm == "FCFS":
        order = requests[:]
        path = [head] + order
    elif algorithm == "SSTF":
        pending = requests[:]
        order, position = [], head
        while pending:
            next_request = min(pending, key=lambda request: abs(request - position))
            order.append(next_request)
            pending.remove(next_request)
            position = next_request
        path = [head] + order
    elif algorithm == "SCAN":
        # The head first moves toward higher-numbered tracks.
        lower = sorted((request for request in requests if request < head), reverse=True)
        upper = sorted(request for request in requests if request >= head)
        order = upper + lower

        # Add the upper disk boundary when the head must reverse to serve lower requests.
        path = [head] + upper
        if lower:
            if not upper or upper[-1] != disk_size - 1:
                path.append(disk_size - 1)
            path.extend(lower)
            if lower[-1] != 0:
                path.append(0)
    else:
        raise ValueError("Algorithm must be FCFS, SSTF or SCAN.")

    movement = sum(abs(path[index + 1] - path[index]) for index in range(len(path) - 1))
    return order, movement


def run_disk_menu():
    requests = [98, 183, 37, 122, 14, 124, 65, 67]
    head = 53
    print("Sample requests:", requests, "| initial head:", head)

    choice = input("Use sample data? (y/n): ").strip().lower()
    if choice == "n":
        requests = [int(value) for value in input("Requests separated by spaces: ").split()]
        head = int(input("Initial head position: "))
    elif choice != "y":
        raise ValueError("Enter y or n.")

    print("1. FCFS  2. SSTF  3. SCAN")
    option = input("Algorithm: ").strip()
    algorithm = {"1": "FCFS", "2": "SSTF", "3": "SCAN"}.get(option)
    if algorithm is None:
        raise ValueError("Invalid disk scheduling algorithm.")

    order, movement = disk_schedule(requests, head, algorithm)
    print("Service order:", " -> ".join(map(str, order)))
    print("Total head movement:", movement, "tracks")
    save_csv(
        "disk_scheduling.csv",
        ["Algorithm", "Service order", "Total head movement"],
        [[algorithm, " -> ".join(map(str, order)), movement]],
    )
    log_event(f"Disk scheduling executed: {algorithm}")
