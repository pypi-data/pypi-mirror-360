from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeAnimationValue (  PptObject) :
    """
    <summary>
        Represent animation point.
    </summary>
    """
    @property
    def Time(self)->float:
        """
    <summary>
        Represents time value.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TimeAnimationValue_get_Time.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValue_get_Time.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TimeAnimationValue_get_Time,self.Ptr)
        return ret

    @Time.setter
    def Time(self, value:float):
        GetDllLibPpt().TimeAnimationValue_set_Time.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TimeAnimationValue_set_Time,self.Ptr, value)

    @property

    def Value(self)->'SpireObject':
        """
    <summary>
        Represents value.
    </summary>
        """
        GetDllLibPpt().TimeAnimationValue_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValue_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeAnimationValue_get_Value,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Value.setter
    def Value(self, value:'SpireObject'):
        GetDllLibPpt().TimeAnimationValue_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TimeAnimationValue_set_Value,self.Ptr, value.Ptr)

    @property

    def Formula(self)->str:
        """
    <summary>
        Formulas values."
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().TimeAnimationValue_get_Formula.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValue_get_Formula.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TimeAnimationValue_get_Formula,self.Ptr))
        return ret


    @Formula.setter
    def Formula(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TimeAnimationValue_set_Formula.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TimeAnimationValue_set_Formula,self.Ptr,valuePtr)

