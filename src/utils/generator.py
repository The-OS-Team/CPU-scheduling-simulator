"""Process generation utilities."""

import random
from src.models.process import Process


def generate_processes(
    num_processes,
    mode="staggered",
    burst_range=(5, 20),
    priority_range=(1, 10),
    seed=42
):
    """
    Unified process generator for all scheduling experiments.
    
    Modes:
        - simultaneous: all arrive at t=0
        - staggered: increasing arrival times
        - random: fully random arrival
        - priority: includes priority-aware dataset
    """


    if seed is not None:
        random.seed(seed)
    processes = []

    for i in range(1, num_processes+1):

        # Arrival logic
        if mode == "simultaneous":
            arrival = 0

        elif mode == "staggered":
            arrival = i  # simple ordered arrival

        elif mode == "random":
            arrival = random.randint(0, num_processes * 2)

        elif mode == "priority":
            arrival = random.randint(0, num_processes)

        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Burst time
        burst = random.randint(*burst_range)

        # Priority (only meaningful for Priority Scheduling)
        priority = random.randint(*priority_range)

        process = Process(
            pid=i,
            arrival_time=arrival,
            burst_time=burst,
            priority=priority
        )

        processes.append(process)

    # Sort by arrival time for deterministic engine behavior
    processes.sort(key=lambda p: p.arrival_time)

    return processes