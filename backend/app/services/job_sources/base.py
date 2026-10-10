from abc import ABC, abstractmethod
from typing import List, Tuple
from app.schemas.job import Job, JobSearchFilter, SourceStatus


class BaseJobSource(ABC):
    """
    Abstract contract for compliant job discovery adapters.
    """
    source_name: str

    @abstractmethod
    async def search(self, filters: JobSearchFilter) -> Tuple[List[Job], SourceStatus]:
        """
        Execute job query without bypassing access barriers.
        Returns a tuple of (normalized jobs list, operational status log).
        """
        pass