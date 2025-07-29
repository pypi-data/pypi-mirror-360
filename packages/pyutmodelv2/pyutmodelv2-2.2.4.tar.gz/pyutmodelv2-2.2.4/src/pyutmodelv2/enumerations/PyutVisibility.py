
from typing import List

from enum import Enum
from typing import cast


class PyutVisibility(Enum):

    PRIVATE   = '-'
    PROTECTED = '#'
    PUBLIC    = '+'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'{self.name} - {self.__str__()}'

    @staticmethod
    def values() -> List[str]:
        retList: List[str] = []
        for valEnum in PyutVisibility:
            val:    PyutVisibility = cast(PyutVisibility, valEnum)
            retList.append(val.__str__())
        return retList

    @staticmethod
    def toEnum(strValue: str) -> 'PyutVisibility':
        """
        Converts the input string to the visibility enum
        Args:
            strValue:   A serialized string value

        Returns:  The visibility enumeration
        """
        canonicalStr: str = strValue.lower().strip(' ')
        if canonicalStr == 'public':
            return PyutVisibility.PUBLIC
        elif canonicalStr == 'private':
            return PyutVisibility.PRIVATE
        elif canonicalStr == 'protected':
            return PyutVisibility.PROTECTED
        elif canonicalStr == '+':
            return PyutVisibility.PUBLIC
        elif canonicalStr == '-':
            return PyutVisibility.PRIVATE
        elif canonicalStr == '#':
            return PyutVisibility.PROTECTED
        else:
            assert False, f'Warning: PyutVisibility.toEnum - Do not recognize visibility type: `{canonicalStr}`'
