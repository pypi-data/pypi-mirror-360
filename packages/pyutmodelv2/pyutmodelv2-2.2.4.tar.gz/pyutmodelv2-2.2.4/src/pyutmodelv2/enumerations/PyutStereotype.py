
from enum import Enum

DEBUG_STEREOTYPE: bool = False


class PyutStereotype(Enum):
    """
    Stereotype Enumeration
    https://www.ibm.com/docs/en/rational-soft-arch/9.5?topic=elements-uml-model-element-stereotypes
    """
    AUXILIARY            = 'auxiliary'
    BOUNDARY             = 'boundary'
    BUILD_COMPONENT      = 'buildComponent'
    CONTROL              = 'control'
    DOCUMENT             = 'document'
    ENTITY               = 'entity'
    EXECUTABLE           = 'executable'
    FILE                 = 'file'
    FOCUS                = 'focus'
    IMPLEMENT            = 'implement'
    IMPLEMENTATION_CLASS = 'implementationClass'
    INTERFACE            = 'interface'
    LIBRARY              = 'library'
    METACLASS            = 'metaclass'
    NODE_TYPE            = 'node type'
    # noinspection SpellCheckingInspection
    POWER_TYPE           = 'powertype'
    REALIZATION          = 'realization'
    SCRIPT               = 'script'
    SERVICE              = 'service'
    SOURCE               = 'source'
    SPECIFICATION        = 'specification'
    SUBSYSTEM            = 'subsystem'
    THREAD               = 'thread'
    TYPE                 = 'type'
    UTILITY              = 'utility'
    ENUMERATION          = 'enumeration'
    NO_STEREOTYPE        = 'noStereotype'

    @classmethod
    def toEnum(cls, strValue: str) -> 'PyutStereotype':
        """
        Converts the input string to the appropriate stereotype

        Args:
            strValue:   A string value

        Returns:  The stereotype enumeration;  Empty strings, multi-spaces strings,
        invalid & None values return PyutStereotype.NO_STEREOTYPE
        """

        if strValue is None:
            canonicalStr: str = ''  # Force to no stereotype
        else:
            canonicalStr = strValue.strip(' ').lower()

        try:
            # noinspection SpellCheckingInspection
            match canonicalStr:
                case 'buildcomponent':
                    stereotype: PyutStereotype = PyutStereotype.BUILD_COMPONENT
                case 'implementationclass':
                    stereotype = PyutStereotype.IMPLEMENTATION_CLASS
                case 'nostereotype':
                    stereotype = PyutStereotype.NO_STEREOTYPE
                case _:
                    stereotype = PyutStereotype(canonicalStr)
        except (ValueError, Exception):
            if DEBUG_STEREOTYPE is True:
                print(f'`{canonicalStr}` coerced to {PyutStereotype.NO_STEREOTYPE}')
            stereotype = PyutStereotype.NO_STEREOTYPE

        return stereotype
