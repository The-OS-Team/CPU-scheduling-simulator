"""Minimum heap implementation."""
import heapq


class MinHeap:
    """Wrapper around heapq for min-heap operations."""
    
    def __init__(self):
        self.heap = []
    
    def push(self, item):
        """Add item to heap."""
        heapq.heappush(self.heap, item)
    
    def pop(self):
        """Remove and return smallest item."""
        if self.heap:
            return heapq.heappop(self.heap)
        return None
    
    def peek(self):
        """Return smallest item without removing."""
        if self.heap:
            return self.heap[0]
        return None
    
    def __len__(self):
        return len(self.heap)
    
    def is_empty(self):
        """Check if heap is empty."""
        return len(self.heap) == 0
