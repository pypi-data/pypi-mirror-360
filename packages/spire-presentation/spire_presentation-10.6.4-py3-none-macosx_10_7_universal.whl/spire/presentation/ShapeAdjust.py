from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAdjust (SpireObject) :
    """
    <summary>
        Represents a shape's adjustment value.
    </summary>
    """
    @property
    def Value(self)->float:
        """
    <summary>
        Gets or sets adjustment value.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ShapeAdjust_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjust_get_Value.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ShapeAdjust_get_Value,self.Ptr)
        return ret

    @Value.setter
    def Value(self, value:float):
        GetDllLibPpt().ShapeAdjust_set_Value.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ShapeAdjust_set_Value,self.Ptr, value)

    @property

    def Name(self)->str:
        """
    <summary>
        Gets a name of this adjustment value.
    </summary>
        """
        GetDllLibPpt().ShapeAdjust_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjust_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ShapeAdjust_get_Name,self.Ptr))
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeAdjust_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeAdjust_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeAdjust_Equals,self.Ptr, intPtrobj)
        return ret

