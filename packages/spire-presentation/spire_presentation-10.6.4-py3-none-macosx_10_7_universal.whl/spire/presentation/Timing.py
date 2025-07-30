from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Timing (  PptObject) :
    """
    <summary>
        Represents animation timing.
    </summary>
    """
    @property
    def Accelerate(self)->float:
        """
    <summary>
        Percentage of the duration over which acceleration should take place
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_Accelerate.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Accelerate.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Accelerate,self.Ptr)
        return ret

    @Accelerate.setter
    def Accelerate(self, value:float):
        GetDllLibPpt().Timing_set_Accelerate.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Accelerate,self.Ptr, value)

    @property
    def Decelerate(self)->float:
        """
    <summary>
        Percentage of the duration over which acceleration should take place
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_Decelerate.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Decelerate.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Decelerate,self.Ptr)
        return ret

    @Decelerate.setter
    def Decelerate(self, value:float):
        GetDllLibPpt().Timing_set_Decelerate.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Decelerate,self.Ptr, value)

    @property
    def AutoReverse(self)->bool:
        """
    <summary>
        Whether an effect should play forward and then reverse, thereby doubling the duration
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_AutoReverse.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_AutoReverse.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Timing_get_AutoReverse,self.Ptr)
        return ret

    @AutoReverse.setter
    def AutoReverse(self, value:bool):
        GetDllLibPpt().Timing_set_AutoReverse.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Timing_set_AutoReverse,self.Ptr, value)

    @property
    def Duration(self)->float:
        """
    <summary>
        Length of animation (in seconds)
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_Duration.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Duration.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Duration,self.Ptr)
        return ret

    @Duration.setter
    def Duration(self, value:float):
        GetDllLibPpt().Timing_set_Duration.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Duration,self.Ptr, value)

    @property
    def RepeatCount(self)->float:
        """
    <summary>
        Describes the number of times the effect should repeat.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_RepeatCount.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_RepeatCount.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_RepeatCount,self.Ptr)
        return ret

    @RepeatCount.setter
    def RepeatCount(self, value:float):
        GetDllLibPpt().Timing_set_RepeatCount.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_RepeatCount,self.Ptr, value)

    @property
    def RepeatDuration(self)->float:
        """
    <summary>
        How long should the repeats last (in seconds)
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_RepeatDuration.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_RepeatDuration.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_RepeatDuration,self.Ptr)
        return ret

    @RepeatDuration.setter
    def RepeatDuration(self, value:float):
        GetDllLibPpt().Timing_set_RepeatDuration.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_RepeatDuration,self.Ptr, value)

    @property

    def Restart(self)->'AnimationRestartType':
        """
    <summary>
        Indicatesif a effect is to restart after complete.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_Restart.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Restart.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Timing_get_Restart,self.Ptr)
        objwraped = AnimationRestartType(ret)
        return objwraped

    @Restart.setter
    def Restart(self, value:'AnimationRestartType'):
        GetDllLibPpt().Timing_set_Restart.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Timing_set_Restart,self.Ptr, value.value)

    @property
    def Speed(self)->float:
        """
    <summary>
        Returns or sets a valeue. 
            specifies the percentage by which to speed up (or slow down) the timing.
    </summary>
        """
        GetDllLibPpt().Timing_get_Speed.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_Speed.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_Speed,self.Ptr)
        return ret

    @Speed.setter
    def Speed(self, value:float):
        GetDllLibPpt().Timing_set_Speed.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_Speed,self.Ptr, value)

    @property
    def TriggerDelayTime(self)->float:
        """
    <summary>
        Delay time from when the trigger is enabled (in seconds)
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_TriggerDelayTime.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_TriggerDelayTime.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Timing_get_TriggerDelayTime,self.Ptr)
        return ret

    @TriggerDelayTime.setter
    def TriggerDelayTime(self, value:float):
        GetDllLibPpt().Timing_set_TriggerDelayTime.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Timing_set_TriggerDelayTime,self.Ptr, value)

    @property

    def TriggerType(self)->'AnimationTriggerType':
        """
    <summary>
        Describes trigger type.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.AnimationTriggerType" />.
    </summary>
        """
        GetDllLibPpt().Timing_get_TriggerType.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_TriggerType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Timing_get_TriggerType,self.Ptr)
        objwraped = AnimationTriggerType(ret)
        return objwraped

    @TriggerType.setter
    def TriggerType(self, value:'AnimationTriggerType'):
        GetDllLibPpt().Timing_set_TriggerType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Timing_set_TriggerType,self.Ptr, value.value)

    @property

    def AnimationRepeatType(self)->'AnimationRepeatType':
        """
    <summary>
        Gets or set repeat type of animation.
    </summary>
        """
        GetDllLibPpt().Timing_get_AnimationRepeatType.argtypes=[c_void_p]
        GetDllLibPpt().Timing_get_AnimationRepeatType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Timing_get_AnimationRepeatType,self.Ptr)
        objwraped = AnimationRepeatType(ret)
        return objwraped

    @AnimationRepeatType.setter
    def AnimationRepeatType(self, value:'AnimationRepeatType'):
        GetDllLibPpt().Timing_set_AnimationRepeatType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Timing_set_AnimationRepeatType,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Timing_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Timing_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Timing_Equals,self.Ptr, intPtrobj)
        return ret

