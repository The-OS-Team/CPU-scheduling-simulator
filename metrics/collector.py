"""Metrics collection for simulation results."""


class Metrics:
    """Collects and tracks process execution metrics."""
    
    def __init__(self):
        self.completed = []
        self.total_time = 0
    
    def record(self, process):
        """Record a completed process."""
        self.completed.append(process)
    
    def set_total_time(self, total_time):
        """Set total simulation time."""
        self.total_time = total_time

    def get_turnaround_time(self, process):
        """Calculate turnaround time for a process."""
        if process.finish_time is None:
            return None
        return process.finish_time - process.arrival_time

    def get_waiting_time(self, process):
        """Calculate waiting time for a process."""
        turnaround = self.get_turnaround_time(process)
        if turnaround is None:
            return None
        return turnaround - process.total_burst

    def get_response_time(self, process):
        """Calculate response time for a process."""
        if process.start_time is None:
            return None
        return process.start_time - process.arrival_time

    def get_avg_turnaround(self):
        """Calculate average turnaround time."""
        if not self.completed:
            return 0
        
        valid_times = [self.get_turnaround_time(p) for p in self.completed if self.get_turnaround_time(p) is not None]
        if not valid_times:
            return 0
        
        total = sum(valid_times)
        return total / len(valid_times)
    
    def get_avg_waiting(self):
        """Calculate average waiting time."""
        if not self.completed:
            return 0
        
        valid_times = [self.get_waiting_time(p) for p in self.completed if self.get_waiting_time(p) is not None]
        if not valid_times:
            return 0
        
        total = sum(valid_times)
        return total / len(valid_times)
    
    def get_avg_response(self):
        """Calculate average response time."""
        if not self.completed:
            return 0
    
        valid = [self.get_response_time(p) for p in self.completed if self.get_response_time(p) is not None]
        if not valid:
            return 0
        
        return sum(valid) / len(valid)
        
    def get_cpu_utilization(self):
        """Calculate CPU utilization."""
        if self.total_time == 0:
            return 0
        
        total_burst = sum(p.total_burst for p in self.completed)
        return (total_burst / self.total_time) * 100

