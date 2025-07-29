
from typing import NewType
from typing import List

from dataclasses import dataclass
from dataclasses import field

from pyutmodelv2.PyutModifier import PyutModifier
from pyutmodelv2.PyutParameter import PyutParameter
from pyutmodelv2.PyutType import PyutType

from pyutmodelv2.enumerations.PyutVisibility import PyutVisibility

from pyutmodelv2.PyutObject import PyutObject

SourceCode     = NewType('SourceCode',     List[str])
PyutModifiers  = NewType('PyutModifiers',  List[PyutModifier])
PyutParameters = NewType('PyutParameters', List[PyutParameter])


def pyutModifiersFactory() -> PyutModifiers:
    return PyutModifiers([])


def sourceCodeFactory() -> SourceCode:
    return SourceCode([])


def parametersFactory() -> PyutParameters:
    return PyutParameters([])


@dataclass
class PyutMethod(PyutObject):
    """
    A method representation.

    A PyutMethod represents a method of a UML class in Pyut. It manages its:

        - parameters (`PyutParameter`)
        - visibility (`PyutVisibility`)
        - modifiers (`PyutModifier`)
        - return type (`PyutType`)
        - source code if reverse-engineered
        - isProperty indicates if the method is really a property
    """
    parameters: PyutParameters = field(default_factory=parametersFactory)
    modifiers:  PyutModifiers  = field(default_factory=pyutModifiersFactory)

    visibility: PyutVisibility  = PyutVisibility.PUBLIC
    returnType: PyutType        = PyutType('')
    isProperty: bool            = False
    sourceCode: SourceCode      = field(default_factory=sourceCodeFactory)

    def addParameter(self, parameter: PyutParameter):
        """
        Add a parameter.

        Args:
            parameter: parameter to add
        """
        self.parameters.append(parameter)

    def methodWithoutParameters(self):
        """
        Returns:   String representation without parameters.
        """
        string = f'{self.visibility}{self.name}()'
        # add the parameters
        if self.returnType.value != "":
            string = f'{string}: {self.returnType}'
        return string

    def methodWithParameters(self):
        """

        Returns: The string representation with parameters
        """
        string = f'{self.visibility}{self.name}('
        # add the params
        if not self.parameters:
            string = f'{string}  '  # to compensate the removing [:-2]
        for param in self.parameters:
            string = f'{string}{param}, '

        string = string[:-2] + ")"      # remove the last comma and add a trailing parenthesis
        if self.returnType.value != "":
            string = f'{string}: {self.returnType}'

        return string

    def __str__(self) -> str:
        """
        Returns: Nice human-readable form
        """
        return self.methodWithParameters()

    def __repr__(self) -> str:
        internalRepresentation: str = (
            f'{self.__str__()} '
            f'{self.modifiers} '
            f'{self.sourceCode}'
        )
        return internalRepresentation


PyutMethods  = NewType('PyutMethods', List[PyutMethod])
