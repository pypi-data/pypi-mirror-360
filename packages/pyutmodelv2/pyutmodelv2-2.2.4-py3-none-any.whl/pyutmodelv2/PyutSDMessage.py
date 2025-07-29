
from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType


@dataclass
class PyutSDMessage(PyutLink):
    message:      str = ''
    sourceY:      int = 0
    destinationY: int = 0
    """
    A message lifeline between two SDInstances.

    """
    def __init__(self, message: str = "", src=None, sourceY: int = 0, dst=None, destinationY: int = 0):

        """

        Args:
            message:        for the message (aka method)
            src:            source of the link
            sourceY:        y location on the source lifeline
            dst:            where the link goes
            destinationY:   y location on the destination lifeline
        """
        self.logger: Logger = getLogger(__name__)

        self.logger.debug(f"PyutSDMessage.__init__ {sourceY}, {destinationY}")
        super().__init__(source=src, destination=dst, linkType=PyutLinkType.SD_MESSAGE)

        self.message      = message
        self.sourceY      = sourceY
        self.destinationY = destinationY

    def __str__(self):
        """

        Returns:    string representing this object
        """
        return f'{self.source} linked to {self.destination}'
