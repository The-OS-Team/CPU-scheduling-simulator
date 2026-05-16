"""Predefined workloads for algorithm analysis."""

from src.models.process import Process


def get_workload(name):
    """
    Deterministic workloads used for discussion and testing.
    """

    workloads = {

        # -----------------------------------------
        # Normal balanced workload
        # -----------------------------------------
        "balanced": [
            Process(1, 0, 8, 3),
            Process(2, 1, 4, 1),
            Process(3, 2, 9, 4),
            Process(4, 3, 5, 2),
        ],

        # -----------------------------------------
        # Priority vs burst conflict
        # -----------------------------------------
        "conflict": [
            Process(1, 0, 20, 1),
            Process(2, 1, 2, 5),
            Process(3, 2, 1, 6),
        ],

        # -----------------------------------------
        # Starvation / fairness example (same brust time, same priority)
        # -----------------------------------------
        "starvation": [
            Process(1, 0, 100, 10),
            
            Process(2, 1, 1, 1),
            Process(3, 2, 1, 1),
            Process(4, 3, 1, 1),
            Process(5, 4, 1, 1),
            Process(6, 5, 1, 1),
        ],


        # -----------------------------------------
        # Tie-breaking validation
        # -----------------------------------------
        "ties": [
            Process(1, 0, 5, 1),
            Process(2, 0, 5, 1),
            Process(3, 0, 5, 1),
        ],


        # -----------------------------------------
        # Simultaneous arrival stress test
        # -----------------------------------------
        "simultaneous": [
            Process(1, 0, 10, 3),
            Process(2, 0, 1, 1),
            Process(3, 0, 2, 2),
            Process(4, 0, 8, 5),
        ],


    }

    if name not in workloads:
        raise ValueError(f"Unknown workload: {name}")

    return workloads[name]
