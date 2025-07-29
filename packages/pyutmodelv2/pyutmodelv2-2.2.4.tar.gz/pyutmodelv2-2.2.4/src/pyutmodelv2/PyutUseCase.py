
from dataclasses import dataclass

from pyutmodelv2.PyutLinkedObject import PyutLinkedObject


@dataclass
class PyutUseCase(PyutLinkedObject):
    """
    """
    def __init__(self, name: str = ''):

        super().__init__(name=name)
