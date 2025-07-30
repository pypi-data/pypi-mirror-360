from enum import Enum


class FinishedReportStatus(str, Enum):
    FINISHED = "finished"

    def __str__(self) -> str:
        return str(self.value)
