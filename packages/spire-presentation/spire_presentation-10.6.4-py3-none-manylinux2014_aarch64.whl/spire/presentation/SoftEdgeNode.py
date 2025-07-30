from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SoftEdgeNode (  EffectNode) :
    """
    <summary>
        Represents a soft edge effect. 
            The edges of the shape are blurred, while the fill is not affected.
    </summary>
    """
    @property
    def Radius(self)->float:
        """
    <summary>
        Specifies the radius of blur to apply to the edges.
    </summary>
        """
        GetDllLibPpt().SoftEdgeNode_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().SoftEdgeNode_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().SoftEdgeNode_get_Radius,self.Ptr)
        return ret

