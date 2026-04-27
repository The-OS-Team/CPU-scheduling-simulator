"""Main simulation engine - time-driven."""

from src.core.clock import Clock
from src.models.state import ProcessState


class Engine:
    """Time-driven simulation engine with strict lifecycle control."""

    def __init__(self, scheduler, processes):
        self.scheduler = scheduler
        self.clock = Clock()

        self.processes = sorted(processes, key=lambda p: p.arrival_time)

        self.arrival_index = 0
        self.current_process = None
        self.timeline = []

    def run(self):
        """Run full simulation."""

        while self._has_remaining_work():
            
            self._handle_arrivals()

            process = self.scheduler.pick_next()
            print("CPU Tick: ", self.clock.get_time())
            print(self.scheduler.queue)
            print("Chosen one:", process)
            if not process:
                self._handle_idle()
                continue

            self._start_process_if_needed(process)
            self._execute(process)

        return self.processes


    def _has_remaining_work(self):
        """System still has unfinished or unarrived work."""
        return (
            self.arrival_index < len(self.processes)
            or self.scheduler.has_work()
        )

    def _handle_arrivals(self):
        """Inject newly arrived processes into scheduler."""

        while (
            self.arrival_index < len(self.processes)
            and self.processes[self.arrival_index].arrival_time <= self.clock.get_time()
        ):
            process = self.processes[self.arrival_index]

            process.state = ProcessState.READY

            self.scheduler.add_process(process)

            self.arrival_index += 1

    def _handle_idle(self):
        """CPU idle period handling."""

        start = self.clock.get_time()
        self.clock.tick(1)
        end = self.clock.get_time()

        self.timeline.append((0, start, end))

    def _start_process_if_needed(self, process):
        """First-time execution bookkeeping."""

        if process.start_time is None:
            process.start_time = self.clock.get_time()

        process.state = ProcessState.RUNNING

    def _execute(self, process):
        """Execute selected process."""

        start = self.clock.get_time()

        delta = self.scheduler.time_slice(process, start)

        end = start + delta

        self.timeline.append((process.pid, start, end))

        # CPU work
        process.remaining_time -= delta
        self.clock.tick(delta)

        # FINISH HANDLED HERE (ENGINE OWNERSHIP)
        if process.remaining_time <= 0:
            process.remaining_time = 0
            process.finish_time = self.clock.get_time()
            process.state = ProcessState.FINISHED

            # IMPORTANT:
            # Do NOT reinsert anywhere
            # Do NOT let scheduler see it again