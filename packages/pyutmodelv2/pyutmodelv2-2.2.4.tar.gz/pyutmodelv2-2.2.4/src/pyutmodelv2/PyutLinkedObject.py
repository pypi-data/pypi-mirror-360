
from typing import Any
from typing import List
from typing import Self

from dataclasses import dataclass
from dataclasses import field

from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutLink import PyutLinks

from pyutmodelv2.PyutObject import PyutObject


def pyutLinksFactory() -> PyutLinks:
    return PyutLinks([])


def parentsFactory() -> List[Any]:
    return []


@dataclass
class PyutLinkedObject(PyutObject):
    """
    An object which can be connected to another one.

    This class provides all support for link management in the data layer. All
    classes that may be interconnected (classes for examples) should inherit
    this class to have all links support.
    """

    links:   PyutLinks  = field(default_factory=pyutLinksFactory, hash=False)
    parents: List[Self] = field(default_factory=parentsFactory,   hash=False)

    def addParent(self, parent: Self):
        """
        Add a parent to the parent list

        Args:
            parent:
        """
        self.parents.append(parent)

    def addLink(self, link: PyutLink):
        """
        Add the given link to the links

        Args:
            link:   The new link to add
        """
        self.links.append(link)

    def __getstate__(self):
        """
        For deepcopy operations, tells which fields to avoid copying.
        Deepcopy must not copy the links to other classes, or it would result
        in copying all the diagram.
        """
        stateDict = self.__dict__.copy()
        stateDict["links"] = []
        return stateDict
