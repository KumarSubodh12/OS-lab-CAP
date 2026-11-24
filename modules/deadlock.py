"""Banker's algorithm safety check for deadlock avoidance."""

from modules.reporting import log_event


def bankers_safety(available, allocation, maximum):
    if not available:
        raise ValueError("At least one resource type is required.")
    if not allocation or len(allocation) != len(maximum):
        raise ValueError("Allocation and maximum matrices must have the same non-zero row count.")

    resource_count = len(available)
    if any(len(row) != resource_count for row in allocation + maximum):
        raise ValueError("Matrix column count must match the available-resource vector.")

    values = list(available)
    values.extend(value for row in allocation + maximum for value in row)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("Resource counts must be non-negative integers.")

    need = [
        [maximum[index][resource] - allocation[index][resource]
         for resource in range(resource_count)]
        for index in range(len(allocation))
    ]
    if any(value < 0 for row in need for value in row):
        raise ValueError("Allocation cannot exceed maximum demand.")

    work = available[:]
    finish = [False] * len(allocation)
    sequence = []

    made_progress = True
    while made_progress:
        made_progress = False
        for index in range(len(allocation)):
            if not finish[index] and all(
                need[index][resource] <= work[resource]
                for resource in range(resource_count)
            ):
                work = [
                    work[resource] + allocation[index][resource]
                    for resource in range(resource_count)
                ]
                finish[index] = True
                sequence.append(f"P{index}")
                made_progress = True

    return all(finish), sequence, need


def run_deadlock_menu():
    # Standard safe-state example: five processes and three resource types.
    available = [3, 3, 2]
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ]
    maximum = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ]

    safe, sequence, need = bankers_safety(available, allocation, maximum)
    print("Available resources:", available)
    print("Need matrix:")
    for index, row in enumerate(need):
        print(f"P{index}: {row}")

    if safe:
        print("System is in a SAFE state. Sequence:", " -> ".join(sequence))
    else:
        print("System is UNSAFE. No complete safe sequence was found.")

    log_event("Banker's safety check executed")
