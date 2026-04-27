"""Simulation runner - glues everything together."""

from src.core.engine import Engine
from src.schedulers.sjf import SJF
from src.schedulers.srtf import SRTF
from src.schedulers.priority import PriorityScheduler

from src.metrics.collector import Metrics
from src.metrics.report import Report
from src.simulation.config import SimulationConfig

from src.utils.generator import generate_processes
from src.utils.validator import validate_processes, validate_config, ValidationError
from src.utils.gantt import plot_gantt

class SimulationRunner:
    """Orchestrates simulation execution."""

    def __init__(self, config=None):
        self.config = config or SimulationConfig()
        self.metrics = Metrics()
        self.timeline = []

    def _create_scheduler(self):
        """Create scheduler based on config."""

        scheduler_type = self.config.scheduler_type.lower()

        if scheduler_type == "sjf":
            return SJF()

        elif scheduler_type in ("srtf", "psjf"):
            return SRTF()

        elif scheduler_type == "priority":
            return PriorityScheduler(True)

        else:
            raise ValueError(f"Unknown scheduler: {self.config.scheduler_type}")

    def run(self):
        """Run simulation."""

        try:
            validate_config(self.config)
            processes = generate_processes(
                self.config.num_processes,
                burst_range=self.config.burst_range,
                priority_range=self.config.priority_range,
                mode=self.config.mode,
                seed=self.config.seed
            )
            validate_processes(processes)

            scheduler = self._create_scheduler()

            engine = Engine(scheduler, processes)
            completed = engine.run()

            self.timeline = engine.timeline

            self.metrics.set_total_time(engine.clock.get_time())

            for p in completed:
                self.metrics.record(p)

            return completed

        except ValidationError as ve:
            print(f"Validation error: {ve}")
            return []

    def get_report(self):
        return Report(self.metrics)

    def print_results(self):
        report = self.get_report()
        report.print_full_report(config=self.config)
        plot_gantt(self.timeline)