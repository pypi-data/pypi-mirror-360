from enum import Enum


class StatusExportedStatus(str, Enum):
    EXPORTED = "exported"

    def __str__(self) -> str:
        return str(self.value)
