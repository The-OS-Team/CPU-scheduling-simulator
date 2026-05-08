"""Configuration for simulation parameters."""


class SimulationConfig:
    """Configuration for simulation runs."""

    def __init__(self):
        self.num_processes = 8
        self.scheduler_type = "srtf"
        self.mode = "simultaneous"
        self.seed = 42

        self.workload = None
        self.burst_range = (5, 20)
        self.priority_range = (1, 10)


    def set_num_processes(self, num):
        self.num_processes = num
        return self

    def set_workload(self, workload):
        self.workload = workload
        return self

    def set_scheduler(self, scheduler_type):
        self.scheduler_type = scheduler_type.lower()
        return self

    def set_mode(self, mode):
        self.mode = mode
        return self

    def set_seed(self, seed):
        self.seed = seed
        return self