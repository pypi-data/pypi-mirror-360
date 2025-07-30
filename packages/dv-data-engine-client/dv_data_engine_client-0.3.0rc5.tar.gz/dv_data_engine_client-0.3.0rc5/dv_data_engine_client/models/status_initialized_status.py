from enum import Enum


class StatusInitializedStatus(str, Enum):
    INITIALIZED = "initialized"

    def __str__(self) -> str:
        return str(self.value)
