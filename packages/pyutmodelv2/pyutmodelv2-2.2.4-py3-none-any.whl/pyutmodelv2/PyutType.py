
from dataclasses import dataclass


@dataclass(frozen=True)
class PyutType:
    value: str = ''

    def __str__(self) -> str:
        """
        String representation.
        """
        return self.value
