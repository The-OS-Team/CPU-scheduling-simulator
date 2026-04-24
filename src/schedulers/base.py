"""Abstract scheduler base class."""

from abc import ABC, abstractmethod


class Scheduler(ABC):
    """Abstract base class for all schedulers."""
    
    @abstractmethod
    def add_process(self, process):
        """Add a process to the ready queue."""
        pass
    
    @abstractmethod
    def pick_next(self, current_time):
        """Pick the next process to run."""
        pass
    
    @abstractmethod
    def time_slice(self, process, current_time):
        """Determine the time slice for a process."""
        pass
    
    @abstractmethod
    def has_work(self):
        """Check if there's any work in the queue."""
        pass
