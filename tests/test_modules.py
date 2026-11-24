import unittest

from modules.cpu_scheduling import fcfs, sjf_non_preemptive, round_robin
from modules.memory_management import allocate
from modules.deadlock import bankers_safety
from modules.disk_scheduling import disk_schedule


class TestCPUScheduling(unittest.TestCase):
    def setUp(self):
        self.processes = [
            {"pid": "P1", "arrival": 0, "burst": 5},
            {"pid": "P2", "arrival": 1, "burst": 3},
        ]

    def test_fcfs_waiting_times(self):
        metrics, schedule = fcfs(self.processes)
        self.assertEqual({row["pid"]: row["waiting"] for row in metrics}, {"P1": 0, "P2": 4})
        self.assertEqual(schedule, [("P1", 0, 5), ("P2", 5, 8)])

    def test_sjf_completes_all_processes(self):
        metrics, schedule = sjf_non_preemptive(self.processes)
        self.assertEqual(len(metrics), 2)
        self.assertEqual(schedule[0], ("P1", 0, 5))

    def test_round_robin_waiting_times(self):
        metrics, _ = round_robin(self.processes, 2)
        self.assertEqual({row["pid"]: row["waiting"] for row in metrics}, {"P1": 3, "P2": 3})

    def test_round_robin_rejects_zero_quantum(self):
        with self.assertRaises(ValueError):
            round_robin(self.processes, 0)

    def test_cpu_rejects_zero_burst_and_duplicate_ids(self):
        with self.assertRaises(ValueError):
            fcfs([{"pid": "P1", "arrival": 0, "burst": 0}])
        with self.assertRaises(ValueError):
            fcfs([
                {"pid": "P1", "arrival": 0, "burst": 1},
                {"pid": "P1", "arrival": 1, "burst": 2},
            ])


class TestMemoryManagement(unittest.TestCase):
    def test_first_fit(self):
        rows, remaining = allocate([100, 300], [80, 150], "First Fit")
        self.assertEqual([row[2] for row in rows], ["B1", "B2"])
        self.assertEqual(remaining, [20, 150])

    def test_best_fit_and_worst_fit(self):
        best, _ = allocate([100, 300, 500], [250], "Best Fit")
        worst, _ = allocate([100, 300, 500], [250], "Worst Fit")
        self.assertEqual(best[0][2], "B2")
        self.assertEqual(worst[0][2], "B3")

    def test_request_that_does_not_fit(self):
        rows, _ = allocate([50], [80], "First Fit")
        self.assertEqual(rows[0][2], "Not allocated")

    def test_invalid_strategy_is_rejected_even_without_fit(self):
        with self.assertRaises(ValueError):
            allocate([10], [100], "Unknown")

    def test_memory_rejects_non_positive_sizes(self):
        with self.assertRaises(ValueError):
            allocate([0], [1], "First Fit")


class TestDeadlock(unittest.TestCase):
    def test_bankers_safe_state(self):
        safe, sequence, need = bankers_safety(
            [3, 3, 2],
            [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]],
            [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
        )
        self.assertTrue(safe)
        self.assertEqual(sequence, ["P1", "P3", "P4", "P0", "P2"])
        self.assertEqual(need[0], [7, 4, 3])

    def test_bankers_detects_unsafe_state(self):
        safe, sequence, _ = bankers_safety([0], [[1]], [[2]])
        self.assertFalse(safe)
        self.assertEqual(sequence, [])

    def test_bankers_rejects_allocation_above_maximum(self):
        with self.assertRaises(ValueError):
            bankers_safety([1], [[2]], [[1]])


class TestDiskScheduling(unittest.TestCase):
    def test_sstf_sample_movement(self):
        order, movement = disk_schedule([98, 183, 37, 122, 14, 124, 65, 67], 53, "SSTF")
        self.assertEqual(order, [65, 67, 37, 14, 98, 122, 124, 183])
        self.assertEqual(movement, 236)

    def test_scan_sample_movement_and_request_order(self):
        order, movement = disk_schedule([98, 183, 37, 122, 14, 124, 65, 67], 53, "SCAN")
        self.assertEqual(order, [65, 67, 98, 122, 124, 183, 37, 14])
        self.assertEqual(movement, 345)

    def test_scan_with_only_lower_requests_reaches_upper_edge(self):
        order, movement = disk_schedule([10, 20], 50, "SCAN", disk_size=100)
        self.assertEqual(order, [20, 10])
        self.assertEqual(movement, 148)

    def test_disk_rejects_out_of_range_track(self):
        with self.assertRaises(ValueError):
            disk_schedule([200], 50, "FCFS", disk_size=200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
