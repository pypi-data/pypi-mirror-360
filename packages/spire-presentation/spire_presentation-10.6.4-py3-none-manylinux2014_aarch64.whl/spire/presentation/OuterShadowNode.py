from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OuterShadowNode (  EffectNode) :
    """
    <summary>
        Represents a outer shadow effect.
    </summary>
    """
    @property
    def BlurRadius(self)->float:
        """
    <summary>
        Blur radius.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_BlurRadius,self.Ptr)
        return ret

    @property
    def Direction(self)->float:
        """
    <summary>
        Direction of shadow.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_Direction,self.Ptr)
        return ret

    @property
    def Distance(self)->float:
        """
    <summary>
        Distance of shadow.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_Distance,self.Ptr)
        return ret

    @property

    def ShadowColor(self)->'Color':
        """
    <summary>
        Color of shadow.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_ShadowColor.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_ShadowColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OuterShadowNode_get_ShadowColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def RectangleAlign(self)->'RectangleAlignment':
        """
    <summary>
        Rectangle alignment.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_RectangleAlign.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_RectangleAlign.restype=c_int
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_RectangleAlign,self.Ptr)
        objwraped = RectangleAlignment(ret)
        return objwraped

    @property
    def SkewHorizontal(self)->float:
        """
    <summary>
        Specifies the horizontal skew angle.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_SkewHorizontal.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_SkewHorizontal.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_SkewHorizontal,self.Ptr)
        return ret

    @property
    def SkewVertical(self)->float:
        """
    <summary>
        Specifies the vertical skew angle.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_SkewVertical.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_SkewVertical.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_SkewVertical,self.Ptr)
        return ret

    @property
    def RotateShadowWithShape(self)->bool:
        """
    <summary>
        Specifies whether the shadow should rotate with the shape if the shape is rotated.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_RotateShadowWithShape.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_RotateShadowWithShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_RotateShadowWithShape,self.Ptr)
        return ret

    @property
    def ScaleHorizontal(self)->float:
        """
    <summary>
        Specifies the horizontal scaling factor, negative scaling causes a flip.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_ScaleHorizontal.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_ScaleHorizontal.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_ScaleHorizontal,self.Ptr)
        return ret

    @property
    def ScaleVertical(self)->float:
        """
    <summary>
        Specifies the vertical scaling factor, negative scaling causes a flip.
    </summary>
        """
        GetDllLibPpt().OuterShadowNode_get_ScaleVertical.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowNode_get_ScaleVertical.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowNode_get_ScaleVertical,self.Ptr)
        return ret

