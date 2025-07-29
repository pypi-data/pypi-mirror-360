
from dataclasses import dataclass
from dataclasses import field

from pyutmodelv2.PyutField import PyutField
from pyutmodelv2.PyutField import PyutFields

from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.PyutMethod import PyutMethods
from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype


def methodsFactory() -> PyutMethods:
    return PyutMethods([])


def fieldsFactory() -> PyutFields:
    return PyutFields([])


@dataclass
class PyutClassCommon:

    description: str = ''
    showMethods: bool = True
    showFields:  bool = True

    displayStereoType: bool = True

    stereotype: PyutStereotype = PyutStereotype.NO_STEREOTYPE

    fields:      PyutFields  = field(default_factory=fieldsFactory)
    methods:     PyutMethods = field(default_factory=methodsFactory)

    def addMethod(self, newMethod: PyutMethod):
        self.methods.append(newMethod)

    def addField(self, pyutField: PyutField):
        """
        Add a field

        Args:
            pyutField:   New field to append

        """
        self.fields.append(pyutField)
