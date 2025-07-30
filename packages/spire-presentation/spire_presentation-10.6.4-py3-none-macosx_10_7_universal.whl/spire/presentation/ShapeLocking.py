from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeLocking (  SimpleShapeBaseLocking) :
    """
    <summary>
        Indicates which operations are disabled on the parent Autoshape.
    </summary>
    """
    @property
    def TextEditingProtection(self)->bool:
        """
    <summary>
        Indicates whether an editing of text Disallow.
    </summary>
        """
        GetDllLibPpt().ShapeLocking_get_TextEditingProtection.argtypes=[c_void_p]
        GetDllLibPpt().ShapeLocking_get_TextEditingProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeLocking_get_TextEditingProtection,self.Ptr)
        return ret

    @TextEditingProtection.setter
    def TextEditingProtection(self, value:bool):
        GetDllLibPpt().ShapeLocking_set_TextEditingProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ShapeLocking_set_TextEditingProtection,self.Ptr, value)

