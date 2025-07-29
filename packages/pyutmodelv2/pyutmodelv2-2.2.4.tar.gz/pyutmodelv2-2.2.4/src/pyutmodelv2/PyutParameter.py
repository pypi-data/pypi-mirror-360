
from dataclasses import dataclass

from pyutmodelv2.PyutObject import PyutObject

from pyutmodelv2.PyutType import PyutType


@dataclass
class PyutParameter(PyutObject):

    # DEFAULT_PARAMETER_NAME: ClassVar = 'parameter'

    type:         PyutType = PyutType("")
    defaultValue: str      = ''

    def __str__(self) -> str:
        """
        We need our own custom representation

        Returns:  String version of a PyutParameter
        """
        s = self.name

        if str(self.type.value) != "":
            s = f'{s}: {self.type.value}'

        if self.defaultValue != '':
            s = f'{s} = {self.defaultValue}'

        return s

    def __repr__(self) -> str:
        return self.__str__()
