from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationProperty (  CommonBehavior) :
    """
    <summary>
        Represent property effect behavior.
    </summary>
    """
    @property

    def From(self)->str:
        """
    <summary>
        Indicates the starting value of the animation.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().AnimationProperty_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_From.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationProperty_get_From,self.Ptr))
        return ret


    @From.setter
    def From(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationProperty_set_From.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_From,self.Ptr,valuePtr)

    @property

    def To(self)->str:
        """
    <summary>
        Indicates the ending value for the animation.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().AnimationProperty_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_To.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationProperty_get_To,self.Ptr))
        return ret


    @To.setter
    def To(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationProperty_set_To.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_To,self.Ptr,valuePtr)

    @property

    def By(self)->str:
        """
    <summary>
        Specifies a relative offset value for the animation.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().AnimationProperty_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_By.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationProperty_get_By,self.Ptr))
        return ret


    @By.setter
    def By(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationProperty_set_By.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_By,self.Ptr,valuePtr)

    @property

    def ValueType(self)->'PropertyValueType':
        """
    <summary>
        Indicates the type of a property value.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.PropertyValueType" />.
    </summary>
        """
        GetDllLibPpt().AnimationProperty_get_ValueType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_ValueType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationProperty_get_ValueType,self.Ptr)
        objwraped = PropertyValueType(ret)
        return objwraped

    @ValueType.setter
    def ValueType(self, value:'PropertyValueType'):
        GetDllLibPpt().AnimationProperty_set_ValueType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_ValueType,self.Ptr, value.value)

    @property

    def CalcMode(self)->'AnimationCalculationMode':
        """
    <summary>
        Indicates the Calculation mode for the animation
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.AnimationCalculationMode" />.
    </summary>
        """
        GetDllLibPpt().AnimationProperty_get_CalcMode.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_CalcMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationProperty_get_CalcMode,self.Ptr)
        objwraped = AnimationCalculationMode(ret)
        return objwraped

    @CalcMode.setter
    def CalcMode(self, value:'AnimationCalculationMode'):
        GetDllLibPpt().AnimationProperty_set_CalcMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_CalcMode,self.Ptr, value.value)

    @property

    def TimeAnimationValueCollection(self)->'TimeAnimationValueCollection':
        """
    <summary>
        Indicates the value of the animation.
            Read/write <see cref="P:Spire.Presentation.Drawing.Animation.AnimationProperty.TimeAnimationValueCollection" />.
    </summary>
        """
        GetDllLibPpt().AnimationProperty_get_TimeAnimationValueCollection.argtypes=[c_void_p]
        GetDllLibPpt().AnimationProperty_get_TimeAnimationValueCollection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationProperty_get_TimeAnimationValueCollection,self.Ptr)
        ret = None if intPtr==None else TimeAnimationValueCollection(intPtr)
        return ret


    @TimeAnimationValueCollection.setter
    def TimeAnimationValueCollection(self, value:'TimeAnimationValueCollection'):
        GetDllLibPpt().AnimationProperty_set_TimeAnimationValueCollection.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationProperty_set_TimeAnimationValueCollection,self.Ptr, value.Ptr)

