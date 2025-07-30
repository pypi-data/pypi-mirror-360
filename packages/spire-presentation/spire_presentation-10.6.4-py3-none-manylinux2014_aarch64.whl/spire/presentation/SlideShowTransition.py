from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideShowTransition (SpireObject) :
    """
    <summary>
        Represents slide show transition.
    </summary>
    """
#    @property
#
#    def WavData(self)->List['Byte']:
#        """
#    <summary>
#        Gets or sets the embedded audio data.
#            Read-only <see cref="T:System.Byte" />[].
#    </summary>
#        """
#        GetDllLibPpt().SlideShowTransition_get_WavData.argtypes=[c_void_p]
#        GetDllLibPpt().SlideShowTransition_get_WavData.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().SlideShowTransition_get_WavData,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret


#    @WavData.setter
#    def WavData(self, value:List['Byte']):
#        vCount = len(value)
#        ArrayType = c_void_p * vCount
#        vArray = ArrayType()
#        for i in range(0, vCount):
#            vArray[i] = value[i].Ptr
#        GetDllLibPpt().SlideShowTransition_set_WavData.argtypes=[c_void_p, ArrayType, c_int]
#        CallCFunction(GetDllLibPpt().SlideShowTransition_set_WavData,self.Ptr, vArray, vCount)


    @property

    def SoundMode(self)->'TransitionSoundMode':
        """
    <summary>
        Set or returns sound mode for slide transition.
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_SoundMode.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_SoundMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_SoundMode,self.Ptr)
        objwraped = TransitionSoundMode(ret)
        return objwraped

    @SoundMode.setter
    def SoundMode(self, value:'TransitionSoundMode'):
        GetDllLibPpt().SlideShowTransition_set_SoundMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_SoundMode,self.Ptr, value.value)

    @property
    def BuiltInSound(self)->bool:
        """
    <summary>
        Specifies whether or not this sound is a built-in sound. If this attribute is set to true then
            the generating application is alerted to check the name attribute specified for this sound
            in it's list of built-in sounds and can then surface a custom name or UI as needed.
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_BuiltInSound.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_BuiltInSound.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_BuiltInSound,self.Ptr)
        return ret

    @BuiltInSound.setter
    def BuiltInSound(self, value:bool):
        GetDllLibPpt().SlideShowTransition_set_BuiltInSound.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_BuiltInSound,self.Ptr, value)

    @property
    def Loop(self)->bool:
        """
    <summary>
        This attribute specifies if the sound will loop until the next sound event occurs in
            slideshow.
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_Loop.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Loop.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Loop,self.Ptr)
        return ret

    @Loop.setter
    def Loop(self, value:bool):
        GetDllLibPpt().SlideShowTransition_set_Loop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Loop,self.Ptr, value)

    @property
    def AdvanceOnClick(self)->bool:
        """
    <summary>
        Specifies whether a mouse click will advance the slide or not. If this attribute is not
            specified then a value of true is assumed
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_AdvanceOnClick.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_AdvanceOnClick.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_AdvanceOnClick,self.Ptr)
        return ret

    @AdvanceOnClick.setter
    def AdvanceOnClick(self, value:bool):
        GetDllLibPpt().SlideShowTransition_set_AdvanceOnClick.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_AdvanceOnClick,self.Ptr, value)

    @property

    def AdvanceAfterTime(self)->'int':
        """
    <summary>
        Specifies the time, in milliseconds, after which the transition should start. This setting
            may be used in conjunction with the advClick attribute. If this attribute is not specified
            then it is assumed that no auto-advance will occur.
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_AdvanceAfterTime.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_AdvanceAfterTime.restype=c_void_p
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_AdvanceAfterTime,self.Ptr)
        return ret


    @AdvanceAfterTime.setter
    def AdvanceAfterTime(self, value:'int'):
        GetDllLibPpt().SlideShowTransition_set_AdvanceAfterTime.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_AdvanceAfterTime,self.Ptr, value)

    @property

    def Speed(self)->'TransitionSpeed':
        """
    <summary>
        Specifies the transition speed that is to be used when transitioning from the current slide
            to the next.
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_Speed.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Speed.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Speed,self.Ptr)
        objwraped = TransitionSpeed(ret)
        return objwraped

    @Speed.setter
    def Speed(self, value:'TransitionSpeed'):
        GetDllLibPpt().SlideShowTransition_set_Speed.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Speed,self.Ptr, value.value)

    @property

    def Duration(self)->'int':
        """
    <summary>
        Specifies the transition duration.take effect above office 2010. 
            millisecond.
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_Duration.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Duration.restype=c_void_p
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Duration,self.Ptr)
        return ret


    @Duration.setter
    def Duration(self, value:'int'):
        GetDllLibPpt().SlideShowTransition_set_Duration.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Duration,self.Ptr, value)

    @property

    def Value(self)->'Transition':
        """
    <summary>
        Slide show transition.
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Value.restype=IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Value,self.Ptr)
        ret = None if intPtrWithTypeName==None else self.CreateTransition(intPtrWithTypeName)
        return ret

    @staticmethod
    def CreateTransition(intPtrWithTypeName:IntPtrWithTypeName)->'Transition':
        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'Spire.Presentation.Drawing.Transition.BlindsSlideTransition'):
            ret = BlindsSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.FlythroughTransition'):
            ret = FlythroughTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.GlitterTransition'):
            ret = GlitterTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.InvXTransition'):
            ret = InvXTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.LRTransition'):
            ret = LRTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.OptionalBlackTransition'):
            ret = OptionalBlackTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.RevealTransition'):
            ret = RevealTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.ShredTransition'):
            ret = ShredTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.SideDirectionTransition'):
            ret = SideDirectionTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.SplitSlideTransition'):
            ret = SplitSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.StripsSlideTransition'):
            ret = StripsSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.WheelSlideTransition'):
            ret = WheelSlideTransition(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Transition.ZoomSlideTransition'):
            ret = ZoomSlideTransition(intPtr)
        else:
            ret = Transition(intPtr)

        return ret

    @property

    def Type(self)->'TransitionType':
        """
    <summary>
        Type of transition
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Type,self.Ptr)
        objwraped = TransitionType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'TransitionType'):
        GetDllLibPpt().SlideShowTransition_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Type,self.Ptr, value.value)

    @property

    def Option(self)->'SpireObject':
        """
    <summary>
        Option of transition
    </summary>
        """
        GetDllLibPpt().SlideShowTransition_get_Option.argtypes=[c_void_p]
        GetDllLibPpt().SlideShowTransition_get_Option.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideShowTransition_get_Option,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Option.setter
    def Option(self, value:'SpireObject'):
        GetDllLibPpt().SlideShowTransition_set_Option.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideShowTransition_set_Option,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SlideShowTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideShowTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideShowTransition_Equals,self.Ptr, intPtrobj)
        return ret

