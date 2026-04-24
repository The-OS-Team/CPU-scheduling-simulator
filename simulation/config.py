"""Configuration for simulation parameters."""


class SimulationConfig:
    """Configuration for simulation runs."""

    def __init__(self):
        self.num_processes = 10
        self.scheduler_type = "sjf"

        self.burst_range = (5, 20)
        self.priority_range = (1, 10)
        self.mode = "simultaneous"

        self.seed = 42

        # optional extensions
        self.time_quantum = 4
        self.sched_latency = 20

    def set_num_processes(self, num):
        self.num_processes = num
        return self

    def set_scheduler(self, scheduler_type):
        self.scheduler_type = scheduler_type.lower()
        return self

    def set_time_quantum(self, quantum):
        self.time_quantum = quantum
        return self

    def set_sched_latency(self, latency):
        self.sched_latency = latency
        return self

    def set_mode(self, mode):
        self.mode = mode
        return self