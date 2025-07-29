
from enum import Enum


class PyutDisplayMethods(Enum):
    """
    Use to indicate if a specific class wishes to display certain
    dunder methods
    """
    UNSPECIFIED    = 'Unspecified'
    DISPLAY        = 'Display'
    DO_NOT_DISPLAY = 'Do Not Display'
