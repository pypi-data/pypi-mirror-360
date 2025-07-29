
from typing import List
from typing import NewType

from dataclasses import dataclass

from pyutmodelv2.PyutParameter import PyutParameter
from pyutmodelv2.PyutType import PyutType

from pyutmodelv2.enumerations.PyutVisibility import PyutVisibility


@dataclass
class PyutField(PyutParameter):
    """
    A class field

    A PyutField represents a UML field
        - parent (`PyutParam`)
        - field  visibility

    Example:
        franField = PyutField("fran", "integer", "55")
        or
        ozzeeField = PyutField('Ozzee', 'str', 'GatoMalo', PyutVisibilityEnum.Private)
    """

    visibility: PyutVisibility = PyutVisibility.PRIVATE

    def __str__(self):
        """
        Need our own custom string value
        Returns:  A nice string
        """

        return f'{self.visibility}{PyutParameter.__str__(self)}'

    def __repr__(self):
        return self.__str__()


PyutFields   = NewType('PyutFields',  List[PyutField])
