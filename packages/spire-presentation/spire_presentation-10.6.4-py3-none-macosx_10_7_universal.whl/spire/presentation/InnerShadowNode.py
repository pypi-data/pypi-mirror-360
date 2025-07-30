from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class InnerShadowNode (  EffectNode) :
    """
    <summary>
        Represents a inner shadow effect.
    </summary>
    """
    @property
    def BlurRadius(self)->float:
        """
    <summary>
        Blur radius.
    </summary>
        """
        GetDllLibPpt().InnerShadowNode_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowNode_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().InnerShadowNode_get_BlurRadius,self.Ptr)
        return ret

    @property
    def Direction(self)->float:
        """
    <summary>
        Direction of shadow.
    </summary>
        """
        GetDllLibPpt().InnerShadowNode_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowNode_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().InnerShadowNode_get_Direction,self.Ptr)
        return ret

    @property
    def Distance(self)->float:
        """
    <summary>
        Distance of shadow.
    </summary>
        """
        GetDllLibPpt().InnerShadowNode_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowNode_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().InnerShadowNode_get_Distance,self.Ptr)
        return ret

    @property

    def ShadowColor(self)->'Color':
        """
    <summary>
        Color of shadow.
    </summary>
        """
        GetDllLibPpt().InnerShadowNode_get_ShadowColor.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowNode_get_ShadowColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().InnerShadowNode_get_ShadowColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


