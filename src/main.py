"""Main entry point for CPU scheduling simulator."""

import argparse

from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner
from src.simulation.comparison import ComparisonRunner


def main():
    print("\nCPU SCHEDULING SIMULATOR")
    print("=" * 70)

    parser = argparse.ArgumentParser(description="CPU Scheduling Simulator")

    parser.add_argument("--p", type=int, default=10)

    parser.add_argument(
        "--sched",
        type=str,
        default="sjf",
        choices=["sjf", "srtf", "priority"],
        help="Scheduler type (used when not comparing)"
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="simultaneous",
        choices=["simultaneous", "random"],
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run SRTF vs Priority comparison"
    )

    args = parser.parse_args()

    config = SimulationConfig()
    config.set_num_processes(args.p)\
          .set_scheduler(args.sched)\
          .set_mode(args.mode)

    # Comparison Mode
    if args.compare:
        print("\n▶️ Running Scheduler Comparison (SRTF vs Priority)")

        runner = ComparisonRunner(config)
        runner.run_all(["srtf", "priority"])
        runner.print_comparison()

    # Single Scheduler Mode
    else:
        print(f"\n▶️ Running {args.sched.upper()} Scheduler")

        runner = SimulationRunner(config)
        runner.run()
        runner.print_results()


if __name__ == "__main__":
    main()
