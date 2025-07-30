from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LinearGradientFill (SpireObject) :
    """

    """
    @property
    def Angle(self)->float:
        """
    <summary>
        Gets or sets the angle of a gradient.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().LinearGradientFill_get_Angle.argtypes=[c_void_p]
        GetDllLibPpt().LinearGradientFill_get_Angle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().LinearGradientFill_get_Angle,self.Ptr)
        return ret

    @Angle.setter
    def Angle(self, value:float):
        GetDllLibPpt().LinearGradientFill_set_Angle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().LinearGradientFill_set_Angle,self.Ptr, value)

    @property

    def IsScaled(self)->'TriState':
        """
    <summary>
        Indicates whether a gradient is scaled.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().LinearGradientFill_get_IsScaled.argtypes=[c_void_p]
        GetDllLibPpt().LinearGradientFill_get_IsScaled.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LinearGradientFill_get_IsScaled,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsScaled.setter
    def IsScaled(self, value:'TriState'):
        GetDllLibPpt().LinearGradientFill_set_IsScaled.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LinearGradientFill_set_IsScaled,self.Ptr, value.value)

