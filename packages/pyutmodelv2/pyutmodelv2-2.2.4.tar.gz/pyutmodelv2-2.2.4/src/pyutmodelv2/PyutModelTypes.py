
from typing import List
from typing import NewType

ClassName    = NewType('ClassName', str)
Implementors = NewType('Implementors', List[ClassName])
