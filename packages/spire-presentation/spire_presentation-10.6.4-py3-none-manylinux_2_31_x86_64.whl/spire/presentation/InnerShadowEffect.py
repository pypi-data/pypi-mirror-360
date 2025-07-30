from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class InnerShadowEffect (SpireObject) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().InnerShadowEffect_CreatInnerShadowEffect.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().InnerShadowEffect_CreatInnerShadowEffect)
        super(InnerShadowEffect, self).__init__(intPtr)
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
        GetDllLibPpt().InnerShadowEffect_get_BlurRadius.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_BlurRadius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_BlurRadius,self.Ptr)
        return ret

    @BlurRadius.setter
    def BlurRadius(self, value:float):
        GetDllLibPpt().InnerShadowEffect_set_BlurRadius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().InnerShadowEffect_set_BlurRadius,self.Ptr, value)

    @property
    def Direction(self)->float:
        """
    <summary>
        Direction of shadow.
    </summary>
        """
        GetDllLibPpt().InnerShadowEffect_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_Direction,self.Ptr)
        return ret

    @Direction.setter
    def Direction(self, value:float):
        GetDllLibPpt().InnerShadowEffect_set_Direction.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().InnerShadowEffect_set_Direction,self.Ptr, value)

    @property
    def Distance(self)->float:
        """
    <summary>
        Distance of shadow.
    </summary>
        """
        GetDllLibPpt().InnerShadowEffect_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:float):
        GetDllLibPpt().InnerShadowEffect_set_Distance.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().InnerShadowEffect_set_Distance,self.Ptr, value)

    @property

    def ColorFormat(self)->'ColorFormat':
        """
    <summary>
        Color of shadow.
    </summary>
        """
        GetDllLibPpt().InnerShadowEffect_get_ColorFormat.argtypes=[c_void_p]
        GetDllLibPpt().InnerShadowEffect_get_ColorFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().InnerShadowEffect_get_ColorFormat,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().InnerShadowEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().InnerShadowEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().InnerShadowEffect_Equals,self.Ptr, intPtrobj)
        return ret

