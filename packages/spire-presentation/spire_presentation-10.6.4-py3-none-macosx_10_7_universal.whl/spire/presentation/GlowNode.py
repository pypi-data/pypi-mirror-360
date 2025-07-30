from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GlowNode (  EffectNode) :
    """
    <summary>
        Represents a glow effect, in which a color blurred outline 
            is added outside the edges of the object.
    </summary>
    """
    @property
    def Radius(self)->float:
        """
    <summary>
        Radius.
    </summary>
        """
        GetDllLibPpt().GlowNode_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().GlowNode_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().GlowNode_get_Radius,self.Ptr)
        return ret

    @property

    def Color(self)->'Color':
        """
    <summary>
        Color.
    </summary>
        """
        GetDllLibPpt().GlowNode_get_Color.argtypes=[c_void_p]
        GetDllLibPpt().GlowNode_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GlowNode_get_Color,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


