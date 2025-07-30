from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommonBehavior (  PptObject) :
    """
    <summary>
        Represent base class behavior of effect.
    </summary>
    """
    @property

    def Accumulate(self)->'TriState':
        """
    <summary>
        Determines whether animation behaviors accumulate.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().CommonBehavior_get_Accumulate.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehavior_get_Accumulate.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehavior_get_Accumulate,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @Accumulate.setter
    def Accumulate(self, value:'TriState'):
        GetDllLibPpt().CommonBehavior_set_Accumulate.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().CommonBehavior_set_Accumulate,self.Ptr, value.value)

    @property

    def Additive(self)->'BehaviorAdditiveType':
        """
    <summary>
        Sets or returns whether the current animation behavior is combined with other running animations. 
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.BehaviorAdditiveType" />.
    </summary>
        """
        GetDllLibPpt().CommonBehavior_get_Additive.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehavior_get_Additive.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehavior_get_Additive,self.Ptr)
        objwraped = BehaviorAdditiveType(ret)
        return objwraped

    @Additive.setter
    def Additive(self, value:'BehaviorAdditiveType'):
        GetDllLibPpt().CommonBehavior_set_Additive.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().CommonBehavior_set_Additive,self.Ptr, value.value)

    @property

    def Timing(self)->'Timing':
        """
    <summary>
        Represents timing properties for the effect behavior.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.Timing" />.
    </summary>
        """
        GetDllLibPpt().CommonBehavior_get_Timing.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehavior_get_Timing.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommonBehavior_get_Timing,self.Ptr)
        ret = None if intPtr==None else Timing(intPtr)
        return ret


    @Timing.setter
    def Timing(self, value:'Timing'):
        GetDllLibPpt().CommonBehavior_set_Timing.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehavior_set_Timing,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CommonBehavior_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CommonBehavior_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CommonBehavior_Equals,self.Ptr, intPtrobj)
        return ret

