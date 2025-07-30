from enum import Enum


class StatusExportingStatus(str, Enum):
    EXPORTING = "exporting"

    def __str__(self) -> str:
        return str(self.value)
