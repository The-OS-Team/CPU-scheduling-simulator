"""Comparison framework for scheduling algorithms."""

import copy

from src.simulation.runner import SimulationRunner
from src.simulation.config import SimulationConfig
from src.utils.gantt import plot_overlay_gantt


class ComparisonRunner:
    """Runs multiple schedulers on the same workload."""

    def __init__(self, base_config):
        self.base_config = base_config
        self.results = {}

    def run_all(self, schedulers):
        """
        schedulers = ["srtf", "priority"]
        """

        base_processes = None

        for scheduler in schedulers:

            config = copy.deepcopy(self.base_config)
            config.set_scheduler(scheduler)

            runner = SimulationRunner(config)

            # IMPORTANT: reuse same generated workload
            if base_processes is None:
                processes = runner.run()
                base_processes = processes
            else:
                # re-run with identical seed if you implemented it
                runner.run()

            report = runner.get_report()

            self.results[scheduler] = {
                "avg_tat": report.metrics.get_avg_turnaround(),
                "avg_wt": report.metrics.get_avg_waiting(),
                "avg_rt": report.metrics.get_avg_response(),
                "cpu": report.metrics.get_cpu_utilization(),
                "timeline": runner.timeline
            }

        return self.results

    def print_comparison(self):
        print("\n" + "=" * 70)
        print("SCHEDULER COMPARISON")
        print("=" * 70)

        for name, data in self.results.items():
            print(f"\n{name.upper()}")
            print(f"Avg TAT: {data['avg_tat']:.2f}")
            print(f"Avg WT : {data['avg_wt']:.2f}")
            print(f"Avg RT : {data['avg_rt']:.2f}")
            print(f"CPU    : {data['cpu']:.2f}%")
        
        plot_overlay_gantt(self.results["srtf"]["timeline"], self.results["priority"]["timeline"])