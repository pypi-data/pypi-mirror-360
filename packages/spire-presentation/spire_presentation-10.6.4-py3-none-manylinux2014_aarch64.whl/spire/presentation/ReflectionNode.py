from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ReflectionNode (  EffectNode) :
    """
    <summary>
        Represents a reflection effect.
    </summary>
    """
    @property
    def StartPosAlpha(self)->float:
        """
    <summary>
        Specifies the start position (along the alpha gradient ramp) of the start alpha value (percents).
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_StartPosAlpha.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_StartPosAlpha.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_StartPosAlpha,self.Ptr)
        return ret

    @property
    def EndPosAlpha(self)->float:
        """
    <summary>
        Specifies the end position (along the alpha gradient ramp) of the end alpha value (percents).
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_EndPosAlpha.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_EndPosAlpha.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_EndPosAlpha,self.Ptr)
        return ret

    @property
    def FadeDirection(self)->float:
        """
    <summary>
        Specifies the direction to offset the reflection. (angle).
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_FadeDirection.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_FadeDirection.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_FadeDirection,self.Ptr)
        return ret

    @property
    def StartReflectionOpacity(self)->float:
        """
    <summary>
        Starting reflection opacity. (percents).
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_StartReflectionOpacity.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_StartReflectionOpacity.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_StartReflectionOpacity,self.Ptr)
        return ret

    @property
    def EndReflectionOpacity(self)->float:
        """
    <summary>
        End reflection opacity. (percents).
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_EndReflectionOpacity.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_EndReflectionOpacity.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_EndReflectionOpacity,self.Ptr)
        return ret

    @property
    def BlurRadius(self)->float:
        """
    <summary>
        Blur radius.
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_BlurRadius,self.Ptr)
        return ret

    @property
    def Direction(self)->float:
        """
    <summary>
        Direction of reflection.
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_Direction,self.Ptr)
        return ret

    @property
    def Distance(self)->float:
        """
    <summary>
        Distance of reflection.
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_Distance,self.Ptr)
        return ret

    @property

    def RectangleAlign(self)->'RectangleAlignment':
        """
    <summary>
        Rectangle alignment.
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_RectangleAlign.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_RectangleAlign.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_RectangleAlign,self.Ptr)
        objwraped = RectangleAlignment(ret)
        return objwraped

    @property
    def SkewH(self)->float:
        """
    <summary>
        Specifies the horizontal skew angle.
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_SkewH.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_SkewH.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_SkewH,self.Ptr)
        return ret

    @property
    def SkewV(self)->float:
        """
    <summary>
        Specifies the vertical skew angle.
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_SkewV.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_SkewV.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_SkewV,self.Ptr)
        return ret

    @property
    def RotateShadowWithShape(self)->bool:
        """
    <summary>
        Specifies whether the reflection should rotate with the shape if the shape is rotated.
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_RotateShadowWithShape.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_RotateShadowWithShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_RotateShadowWithShape,self.Ptr)
        return ret

    @property
    def ScaleH(self)->float:
        """
    <summary>
        Specifies the horizontal scaling factor, negative scaling causes a flip. (percents)
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_ScaleH.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_ScaleH.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_ScaleH,self.Ptr)
        return ret

    @property
    def ScaleV(self)->float:
        """
    <summary>
        Specifies the vertical scaling factor, negative scaling causes a flip. (percents)
    </summary>
        """
        GetDllLibPpt().ReflectionNode_get_ScaleV.argtypes=[c_void_p]
        GetDllLibPpt().ReflectionNode_get_ScaleV.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ReflectionNode_get_ScaleV,self.Ptr)
        return ret

