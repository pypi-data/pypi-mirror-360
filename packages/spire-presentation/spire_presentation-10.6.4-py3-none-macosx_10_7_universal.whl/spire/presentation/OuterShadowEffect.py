from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OuterShadowEffect (SpireObject) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().OuterShadowEffect_Creat.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OuterShadowEffect_Creat)
        super(OuterShadowEffect, self).__init__(intPtr)
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
        GetDllLibPpt().OuterShadowEffect_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_BlurRadius,self.Ptr)
        return ret

    @BlurRadius.setter
    def BlurRadius(self, value:float):
        GetDllLibPpt().OuterShadowEffect_set_BlurRadius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_BlurRadius,self.Ptr, value)

    @property
    def Direction(self)->float:
        """
    <summary>
        Direction of shadow.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_Direction,self.Ptr)
        return ret

    @Direction.setter
    def Direction(self, value:float):
        GetDllLibPpt().OuterShadowEffect_set_Direction.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_Direction,self.Ptr, value)

    @property
    def Distance(self)->float:
        """
    <summary>
        Distance of shadow.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:float):
        GetDllLibPpt().OuterShadowEffect_set_Distance.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_Distance,self.Ptr, value)

    @property

    def ColorFormat(self)->'ColorFormat':
        """
    <summary>
        Color of shadow.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_ColorFormat.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_ColorFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_ColorFormat,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def RectangleAlign(self)->'RectangleAlignment':
        """
    <summary>
        Rectangle alignment.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_RectangleAlign.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_RectangleAlign.restype=c_int
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_RectangleAlign,self.Ptr)
        objwraped = RectangleAlignment(ret)
        return objwraped

    @RectangleAlign.setter
    def RectangleAlign(self, value:'RectangleAlignment'):
        GetDllLibPpt().OuterShadowEffect_set_RectangleAlign.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_RectangleAlign,self.Ptr, value.value)

    @property
    def HorizontalSkew(self)->float:
        """
    <summary>
        Specifies the horizontal skew angle.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_HorizontalSkew.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_HorizontalSkew.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_HorizontalSkew,self.Ptr)
        return ret

    @HorizontalSkew.setter
    def HorizontalSkew(self, value:float):
        GetDllLibPpt().OuterShadowEffect_set_HorizontalSkew.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_HorizontalSkew,self.Ptr, value)

    @property
    def VerticalSkew(self)->float:
        """
    <summary>
        Specifies the vertical skew angle.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_VerticalSkew.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_VerticalSkew.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_VerticalSkew,self.Ptr)
        return ret

    @VerticalSkew.setter
    def VerticalSkew(self, value:float):
        GetDllLibPpt().OuterShadowEffect_set_VerticalSkew.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_VerticalSkew,self.Ptr, value)

    @property
    def RotateWithShape(self)->bool:
        """
    <summary>
        Specifies whether the shadow should rotate with the shape if the shape is rotated.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_RotateWithShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_RotateWithShape,self.Ptr)
        return ret

    @RotateWithShape.setter
    def RotateWithShape(self, value:bool):
        GetDllLibPpt().OuterShadowEffect_set_RotateWithShape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_RotateWithShape,self.Ptr, value)

    @property
    def HorizontalScalingFactor(self)->float:
        """
    <summary>
        Specifies the horizontal scaling factor, negative scaling causes a flip.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_HorizontalScalingFactor.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_HorizontalScalingFactor.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_HorizontalScalingFactor,self.Ptr)
        return ret

    @HorizontalScalingFactor.setter
    def HorizontalScalingFactor(self, value:float):
        GetDllLibPpt().OuterShadowEffect_set_HorizontalScalingFactor.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_HorizontalScalingFactor,self.Ptr, value)

    @property
    def VerticalScalingFactor(self)->float:
        """
    <summary>
        Specifies the vertical scaling factor, negative scaling causes a flip.
    </summary>
        """
        GetDllLibPpt().OuterShadowEffect_get_VerticalScalingFactor.argtypes=[c_void_p]
        GetDllLibPpt().OuterShadowEffect_get_VerticalScalingFactor.restype=c_float
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_get_VerticalScalingFactor,self.Ptr)
        return ret

    @VerticalScalingFactor.setter
    def VerticalScalingFactor(self, value:float):
        GetDllLibPpt().OuterShadowEffect_set_VerticalScalingFactor.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().OuterShadowEffect_set_VerticalScalingFactor,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().OuterShadowEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().OuterShadowEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OuterShadowEffect_Equals,self.Ptr, intPtrobj)
        return ret

