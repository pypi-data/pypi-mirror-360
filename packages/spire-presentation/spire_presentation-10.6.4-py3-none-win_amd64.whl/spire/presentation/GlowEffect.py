from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GlowEffect (SpireObject) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().GlowEffect_CreatGlowEffect.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GlowEffect_CreatGlowEffect)
        super(GlowEffect, self).__init__(intPtr)
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
        GetDllLibPpt().GlowEffect_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().GlowEffect_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().GlowEffect_get_Radius,self.Ptr)
        return ret

    @Radius.setter
    def Radius(self, value:float):
        GetDllLibPpt().GlowEffect_set_Radius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().GlowEffect_set_Radius,self.Ptr, value)

    @property

    def ColorFormat(self)->'ColorFormat':
        """
    <summary>
        Color format.
    </summary>
        """
        GetDllLibPpt().GlowEffect_get_ColorFormat.argtypes=[c_void_p]
        GetDllLibPpt().GlowEffect_get_ColorFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GlowEffect_get_ColorFormat,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GlowEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GlowEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GlowEffect_Equals,self.Ptr, intPtrobj)
        return ret

