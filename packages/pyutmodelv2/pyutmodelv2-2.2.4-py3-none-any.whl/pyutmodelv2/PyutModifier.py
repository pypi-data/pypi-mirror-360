
from dataclasses import dataclass


@dataclass(frozen=True)
class PyutModifier:
    """
    Modifier for a method or a parameter.
    These are words like:

    * "abstract"
    * "virtual"
    * "const"
    """
    name: str = ''

    def __str__(self) -> str:
        """
        Returns:
            String representation.
        """
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
