from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationCommandBehavior (  CommonBehavior) :
    """
    <summary>
        Represents a command effect for an animation behavior.
    </summary>
    """
    @property

    def Type(self)->'AnimationCommandType':
        """
    <summary>
        Indicates command type of behavior.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.AnimationCommandType" />.
    </summary>
        """
        GetDllLibPpt().AnimationCommandBehavior_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().AnimationCommandBehavior_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationCommandBehavior_get_Type,self.Ptr)
        objwraped = AnimationCommandType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'AnimationCommandType'):
        GetDllLibPpt().AnimationCommandBehavior_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationCommandBehavior_set_Type,self.Ptr, value.value)

    @property

    def Value(self)->str:
        """
    <summary>
        Indicates command value.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().AnimationCommandBehavior_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().AnimationCommandBehavior_get_Value.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationCommandBehavior_get_Value,self.Ptr))
        return ret


    @Value.setter
    def Value(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationCommandBehavior_set_Value.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationCommandBehavior_set_Value,self.Ptr,valuePtr)

    @property

    def Target(self)->'IShape':
        """
    <summary>
        Indicates shape target.
            Read/write <see cref="T:Spire.Presentation.Shape" />.
    </summary>
        """
        GetDllLibPpt().AnimationCommandBehavior_get_Target.argtypes=[c_void_p]
        GetDllLibPpt().AnimationCommandBehavior_get_Target.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationCommandBehavior_get_Target,self.Ptr)
        ret = None if intPtr==None else IShape(intPtr)
        return ret


