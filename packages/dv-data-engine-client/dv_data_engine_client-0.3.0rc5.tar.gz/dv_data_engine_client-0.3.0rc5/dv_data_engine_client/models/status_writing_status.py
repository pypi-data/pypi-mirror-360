from enum import Enum


class StatusWritingStatus(str, Enum):
    WRITING = "writing"

    def __str__(self) -> str:
        return str(self.value)
