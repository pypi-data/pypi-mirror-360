from enum import Enum


class FinishedSummaryStatus(str, Enum):
    FINISHED = "finished"

    def __str__(self) -> str:
        return str(self.value)
