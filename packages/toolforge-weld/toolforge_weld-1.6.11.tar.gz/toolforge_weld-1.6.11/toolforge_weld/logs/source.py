from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterator, Optional


@dataclass(frozen=True)
class LogEntry:
    """Represents a single log entry."""

    pod: str
    container: str

    datetime: datetime
    message: str


class LogSource(metaclass=ABCMeta):
    """Queries logs from a remote source."""

    @abstractmethod
    def query(
        self, *, selector: Dict[str, str], follow: bool, lines: Optional[int]
    ) -> Iterator[LogEntry]:
        pass
