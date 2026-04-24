"""Global time management for the simulation."""


class Clock:
    """Manages simulation time."""
    
    def __init__(self):
        self.current_time = 0
    
    def tick(self, delta=1):
        """Advance the clock."""
        self.current_time += delta
        return self.current_time
    
    def get_time(self):
        """Get current simulation time."""
        return self.current_time
    
    def reset(self):
        """Reset clock to zero."""
        self.current_time = 0
