"""
This module contains all structures like data class, enums
"""
import time
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class WorkerStats:
    """
    Each thread will have its own stats
    """
    total_files_processed: int = 0
    total_files_size: int = 0
    total_file_sort_failed: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    def done(self) -> None:
        self.end_time = time.time()

    def duration(self) -> time:
        return self.end_time - self.start_time if self.end_time else time.time() - self.start_time

    def throughput(self) -> float:
        duration = self.duration()
        return self.total_files_processed / duration if duration > 0 else 0.0

@dataclass
class FileDate:
    """
    Will be used while extracting file meta
    """
    year: str
    month: str
    day: str


class ProcessType(Enum):
    """
    to execute in a manner
    """
    LINEAR = 'linear'
    PARALLEL = 'parallel'

class NestedOrder(Enum):
    """
    Will be used while extracting file meta
    """
    ALPHABET = 'alphabet'
    DATE = 'date'
    FILE_EXTENSION = 'file_extension'
    FILE_EXTENSION_GROUP = 'file_extension_group'
    # LOCATION = 'location'
    MAKE = 'make'
    MODEL = 'model'

class ShiftType(Enum):
    """
    using string enum for readable
    """
    COPY = 'copy'
    MOVE = 'move'

