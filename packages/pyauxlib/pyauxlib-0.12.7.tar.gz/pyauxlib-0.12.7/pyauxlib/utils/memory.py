"""Basic memory tracker."""

import tracemalloc
from tracemalloc import Snapshot, StatisticDiff

try:
    from typing import Self  # Only works from Python 3.11
except ImportError:
    from typing_extensions import Self


class MemoryTracker:
    """Basic memory tracker to measure memory usage.

    It can be used as a context manager:
    ```python
    with MemoryTracker() as mt:
        # code here
    print(f'Peak memory usage: {mt.get_peak_memory_usage()}')
    ```

    Attributes
    ----------
    start_snapshot : tracemalloc.Snapshot or None
        The snapshot of the memory usage at the start of the context manager.
    stop_snapshot : tracemalloc.Snapshot or None
        The snapshot of the memory usage at the end of the context manager.
    peak : int
        The peak memory usage during the execution of the code block.
    """

    def __init__(self) -> None:
        self.start_snapshot: Snapshot | None = None
        self.stop_snapshot: Snapshot | None = None
        self.peak: int = 0

    def __enter__(self) -> Self:
        """Start a new MemoryTracker as a context manager."""
        tracemalloc.start()
        self.start_snapshot = tracemalloc.take_snapshot()
        return self

    def __exit__(self, *args: object) -> None:
        """Stop the context manager MemoryTracker."""
        self.stop_snapshot = tracemalloc.take_snapshot()
        self.peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()

    def get_peak_memory_usage(self) -> int:
        """Get the peak memory usage during the execution of the code block.

        Returns
        -------
        int
            The peak memory usage in bytes.
        """
        return self.peak

    def get_memory_diff(self) -> list[StatisticDiff] | None:
        """Get the difference in memory usage between the start and stop snapshots.

        Returns
        -------
        list of tracemalloc.StatisticDiff or None
            The list of statistics about the change in memory usage between the start and stop
            snapshots.
            Returns None if either start_snapshot or stop_snapshot is None.
        """
        if not self.start_snapshot or not self.stop_snapshot:
            return None
        return self.stop_snapshot.compare_to(self.start_snapshot, "lineno")
