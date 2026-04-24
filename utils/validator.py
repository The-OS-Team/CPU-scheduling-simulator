class ValidationError(Exception):
    pass


def validate_processes(processes):
    """Validate list of processes before simulation."""
    
    seen_pids = set()

    for p in processes:
        # PID check
        if p.pid in seen_pids:
            raise ValidationError(f"Duplicate PID detected: {p.pid}")
        seen_pids.add(p.pid)

        # Arrival time
        if p.arrival_time < 0:
            raise ValidationError(f"Invalid arrival time for PID {p.pid}")

        # Burst time
        if p.total_burst <= 0:
            raise ValidationError(f"Invalid burst time for PID {p.pid}")

        # Optional safety
        if p.total_burst is None:
            raise ValidationError(f"Missing burst time for PID {p.pid}")
        

def validate_config(config):
    """Validate simulation configuration."""

    if config.num_processes <= 0:
        raise ValidationError("Number of processes must be > 0")

    if config.scheduler_type.lower() == "rr":
        if config.time_quantum is None or config.time_quantum <= 0:
            raise ValidationError("RR requires time_quantum > 0")

    if config.scheduler_type.lower() not in ["sjf","srtf","priority"]:
        raise ValidationError(f"Unknown scheduler: {config.scheduler_type}")