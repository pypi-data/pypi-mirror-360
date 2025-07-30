from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlurNode (  EffectNode) :
    """
    <summary>
        Represents a Blur effect that is applied to the entire shape, including its fill.
            All color channels, including alpha, are affected.
    </summary>
    """
    @property
    def Radius(self)->float:
        """
    <summary>
        Blur radius.
            Readonly <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().BlurNode_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().BlurNode_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().BlurNode_get_Radius,self.Ptr)
        return ret

    @property
    def Grow(self)->bool:
        """
    <summary>
        Indicates whether effect spreads beyond shape border.
            Readonly <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().BlurNode_get_Grow.argtypes=[c_void_p]
        GetDllLibPpt().BlurNode_get_Grow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BlurNode_get_Grow,self.Ptr)
        return ret

