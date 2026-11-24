"""Contiguous variable-sized memory allocation strategies."""

from modules.reporting import save_csv, log_event

STRATEGIES = {"First Fit", "Best Fit", "Worst Fit"}


def allocate(blocks, requests, strategy):
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown allocation strategy. Choose one of: {', '.join(sorted(STRATEGIES))}.")
    if not blocks:
        raise ValueError("At least one memory block is required.")
    if not requests:
        raise ValueError("At least one memory request is required.")

    free = [int(size) for size in blocks]
    sizes = [int(size) for size in requests]
    if any(size <= 0 for size in free + sizes):
        raise ValueError("Memory block sizes and requests must be positive.")

    results = []
    for request_index, size in enumerate(sizes, 1):
        candidates = [index for index, available in enumerate(free) if available >= size]
        chosen = None

        if candidates:
            if strategy == "First Fit":
                chosen = candidates[0]
            elif strategy == "Best Fit":
                chosen = min(candidates, key=lambda index: free[index])
            else:
                chosen = max(candidates, key=lambda index: free[index])
            free[chosen] -= size

        results.append([
            f"R{request_index}",
            size,
            f"B{chosen + 1}" if chosen is not None else "Not allocated",
            free[chosen] if chosen is not None else "—",
        ])

    return results, free


def run_memory_menu():
    blocks = [100, 500, 200, 300, 600]
    requests = [212, 417, 112, 426]
    print("Default blocks:", blocks, "| requests:", requests)

    choice = input("Use sample data? (y/n): ").strip().lower()
    if choice == "n":
        blocks = [int(value) for value in input("Enter block sizes separated by spaces: ").split()]
        requests = [int(value) for value in input("Enter request sizes separated by spaces: ").split()]
    elif choice != "y":
        raise ValueError("Enter y or n.")

    print("1. First Fit  2. Best Fit  3. Worst Fit")
    option = input("Strategy: ").strip()
    strategy = {"1": "First Fit", "2": "Best Fit", "3": "Worst Fit"}.get(option)
    if strategy is None:
        raise ValueError("Invalid memory strategy.")

    rows, remaining = allocate(blocks, requests, strategy)
    print(f"\n{strategy} allocation")
    print(f"{'Request':<10}{'Size':<10}{'Block':<18}{'Remaining':<10}")
    for row in rows:
        print(f"{row[0]:<10}{row[1]:<10}{row[2]:<18}{row[3]}")

    print("Remaining block capacities:", remaining)
    save_csv(
        "memory_allocation.csv",
        ["Request", "Size", "Block", "Remaining capacity"],
        rows,
    )
    log_event(f"Memory allocation executed: {strategy}")
