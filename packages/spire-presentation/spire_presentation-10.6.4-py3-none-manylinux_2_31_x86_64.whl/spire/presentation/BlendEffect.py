from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlendEffect ( IActiveSlide ) :
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
        Gets or sets blur radius.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().BlendEffect_get_Radius.argtypes=[c_void_p]
        GetDllLibPpt().BlendEffect_get_Radius.restype=c_double
        ret = CallCFunction(GetDllLibPpt().BlendEffect_get_Radius,self.Ptr)
        return ret

    @Radius.setter
    def Radius(self, value:float):
        GetDllLibPpt().BlendEffect_set_Radius.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().BlendEffect_set_Radius,self.Ptr, value)

    @property
    def IsGrow(self)->bool:
        """
    <summary>
        Indicates whether the bounds of the object should be grown as a result of the blurring.
            True indicates the bounds are grown while false indicates that they are not.
    </summary>
        """
        GetDllLibPpt().BlendEffect_get_IsGrow.argtypes=[c_void_p]
        GetDllLibPpt().BlendEffect_get_IsGrow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BlendEffect_get_IsGrow,self.Ptr)
        return ret

    @IsGrow.setter
    def IsGrow(self, value:bool):
        GetDllLibPpt().BlendEffect_set_IsGrow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().BlendEffect_set_IsGrow,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().BlendEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().BlendEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BlendEffect_Equals,self.Ptr, intPtrobj)
        return ret

