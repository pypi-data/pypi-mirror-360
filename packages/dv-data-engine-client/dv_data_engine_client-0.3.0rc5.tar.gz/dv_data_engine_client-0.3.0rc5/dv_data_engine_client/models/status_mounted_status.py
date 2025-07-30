from enum import Enum


class StatusMountedStatus(str, Enum):
    MOUNTED = "mounted"

    def __str__(self) -> str:
        return str(self.value)
