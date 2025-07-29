
from typing import Dict
from typing import List
from typing import NewType

from dataclasses import dataclass
# from dataclasses import field

from pyutmodelv2.PyutModelTypes import ClassName
from pyutmodelv2.PyutModelTypes import Implementors

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutClassCommon import PyutClassCommon


def implementorsFactory() -> Implementors:
    return Implementors([])


@dataclass
class PyutInterface(PyutObject, PyutClassCommon):

    def __init__(self, name: str = ''):
        """

        Args:
            name:  The interface name
        """
        super().__init__(name=name)
        PyutClassCommon.__init__(self)

        self._implementors: Implementors = Implementors([])

    @property
    def implementors(self) -> Implementors:
        return self._implementors

    @implementors.setter
    def implementors(self, newValue: Implementors):
        self._implementors = newValue

    def addImplementor(self, newClassName: ClassName):
        self.implementors.append(newClassName)

    def __hash__(self) -> int:
        return hash((self.name, self.id))

    def __eq__(self, other) -> bool:
        """

             Args:
                 other:

             Returns:  True if the defined PointNodes are 'functionally' equal
        """
        ans: bool = False

        if isinstance(other, PyutInterface) is False:
            pass
        else:
            if self.name == other.name and self.id == other.id :
                ans = True

        return ans

    def __repr__(self):

        methodsStr = ''
        for method in self.methods:
            methodsStr = f'{methodsStr} {method} '

        return f'PyutInterface {self.name} {methodsStr}'


PyutInterfaces     = NewType('PyutInterfaces',     List[PyutInterface])
PyutInterfacesDict = NewType('PyutInterfacesDict', Dict[str, PyutInterface])
