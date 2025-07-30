from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationColorTransform (SpireObject) :
    """
    <summary>
        Represent color offset.
    </summary>
    """
    @property
    def Color1(self)->float:
        """
    <summary>
        Defines first value of color.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().AnimationColorTransform_get_Color1.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorTransform_get_Color1.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationColorTransform_get_Color1,self.Ptr)
        return ret

    @Color1.setter
    def Color1(self, value:float):
        GetDllLibPpt().AnimationColorTransform_set_Color1.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationColorTransform_set_Color1,self.Ptr, value)

    @property
    def Color2(self)->float:
        """
    <summary>
        Defines second value of color.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().AnimationColorTransform_get_Color2.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorTransform_get_Color2.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationColorTransform_get_Color2,self.Ptr)
        return ret

    @Color2.setter
    def Color2(self, value:float):
        GetDllLibPpt().AnimationColorTransform_set_Color2.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationColorTransform_set_Color2,self.Ptr, value)

    @property
    def Color3(self)->float:
        """
    <summary>
        Defines third value of color.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().AnimationColorTransform_get_Color3.argtypes=[c_void_p]
        GetDllLibPpt().AnimationColorTransform_get_Color3.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationColorTransform_get_Color3,self.Ptr)
        return ret

    @Color3.setter
    def Color3(self, value:float):
        GetDllLibPpt().AnimationColorTransform_set_Color3.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationColorTransform_set_Color3,self.Ptr, value)

