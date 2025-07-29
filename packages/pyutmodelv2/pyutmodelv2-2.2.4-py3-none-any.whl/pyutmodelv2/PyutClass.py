
from typing import Dict
from typing import List
from typing import NewType

from dataclasses import dataclass
from dataclasses import field

from pyutmodelv2.PyutClassCommon import PyutClassCommon
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutInterface import PyutInterfaces
from pyutmodelv2.PyutLinkedObject import PyutLinkedObject
from pyutmodelv2.enumerations.PyutDisplayMethods import PyutDisplayMethods

from pyutmodelv2.enumerations.PyutDisplayParameters import PyutDisplayParameters
from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype


def pyutInterfacesFactory() -> PyutInterfaces:
    return PyutInterfaces([])


@dataclass
class PyutClass(PyutLinkedObject, PyutClassCommon):
    """
    A standard class representation.

    A PyutClass represents a UML class in Pyut. It manages its:
        - object data fields (`PyutField`)
        - methods (`PyutMethod`)
        - parents (`PyutClass`)(classes from which this one inherits)
        - stereotype (`PyutStereotype`)
        - a description (`string`)

    Example:
        ```python
            myClass = PyutClass("Foo") # this will create a `Foo` class
            myClass.description = "Example class"

            fields = myClass.fields             # These are the original fields, not a copy
            fields.append(PyutField(name="bar", fieldType="int"))
        ```

    Correct multiple inheritance:
        https://stackoverflow.com/questions/59986413/achieving-multiple-inheritance-using-python-dataclasses
    """
    displayParameters:    PyutDisplayParameters = PyutDisplayParameters.UNSPECIFIED
    displayConstructor:   PyutDisplayMethods    = PyutDisplayMethods.UNSPECIFIED
    displayDunderMethods: PyutDisplayMethods    = PyutDisplayMethods.UNSPECIFIED
    interfaces:           PyutInterfaces        = field(default_factory=pyutInterfacesFactory)

    def __post_init__(self):
        super().__post_init__()
        PyutClassCommon.__init__(self)

    def addInterface(self, pyutInterface: PyutInterface):
        self.interfaces.append(pyutInterface)

    def __getstate__(self):
        """
        For deepcopy operations, specifies which fields to avoid copying.
        Deepcopy must not copy the links to other classes, or it would result
        in copying the entire diagram.
        """
        aDict = self.__dict__.copy()
        aDict["parents"]    = []
        return aDict

    def __str__(self):
        """
        String representation.
        """
        return f"Class : {self.name}"

    def __repr__(self):
        return self.__str__()


PyutClassName = NewType('PyutClassName',  str)

PyutClassList  = NewType('PyutClassList',    List[PyutClass])
PyutClassIndex = NewType('PyutClassIndex', Dict[PyutClassName, PyutClass])
