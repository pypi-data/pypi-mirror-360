
from enum import Enum

from dataclasses import dataclass

from pyutmodelv2.PyutObject import PyutObject


class PyutSDInstanceType(Enum):
    INSTANCE_TYPE_ACTOR = 'Actor'
    INSTANCE_TYPE_CLASS = 'Class'


@dataclass
class PyutSDInstance(PyutObject):
    instanceName:           str = "Unnamed instance"
    instanceLifeLineLength: int = 200
    instanceGraphicalType:  PyutSDInstanceType = PyutSDInstanceType.INSTANCE_TYPE_CLASS
    """
    Data model representation of a UML Collaboration instance (C.Diagram).
    """
