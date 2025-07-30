from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNodeAudio (  TimeNodeMedia) :
    """

    """
#    @dispatch
#
#    def SetAudioData(self ,file:'FileInfo'):
#        """
#    <summary>
#        setTimeNodeAudio
#    </summary>
#    <param name="file">audio file</param>
#        """
#        intPtrfile:c_void_p = file.Ptr
#
#        GetDllLibPpt().TimeNodeAudio_SetAudioData.argtypes=[c_void_p ,c_void_p]
#        CallCFunction(GetDllLibPpt().TimeNodeAudio_SetAudioData,self.Ptr, intPtrfile)


    @dispatch

    def SetAudioData(self ,stream:Stream):
        """
    <summary>
        Set Audio Data.
    </summary>
    <param name="stream"></param>
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().TimeNodeAudio_SetAudioData.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().TimeNodeAudio_SetAudioData,self.Ptr, intPtrstream)


    def GetAudioData(self)->List['Byte']:
        """
    <summary>
        GetTimeNodeAudio : get audio bytes
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().TimeNodeAudio_GetAudioData.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_GetAudioData.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().TimeNodeAudio_GetAudioData,self.Ptr)
        ret = GetBytesFromArray(intPtrArray)
        return ret


    @property
    def Volume(self)->float:
        """
    <summary>
        Volume :value range 0 - 1
    </summary>
        """
        GetDllLibPpt().TimeNodeAudio_get_Volume.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_get_Volume.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TimeNodeAudio_get_Volume,self.Ptr)
        return ret

    @Volume.setter
    def Volume(self, value:float):
        GetDllLibPpt().TimeNodeAudio_set_Volume.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TimeNodeAudio_set_Volume,self.Ptr, value)

    @property
    def IsMute(self)->bool:
        """
    <summary>
        is mute default:false
    </summary>
        """
        GetDllLibPpt().TimeNodeAudio_get_IsMute.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_get_IsMute.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNodeAudio_get_IsMute,self.Ptr)
        return ret

    @IsMute.setter
    def IsMute(self, value:bool):
        GetDllLibPpt().TimeNodeAudio_set_IsMute.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TimeNodeAudio_set_IsMute,self.Ptr, value)

    @property

    def SoundName(self)->str:
        """
    <summary>
        SoundName
    </summary>
        """
        GetDllLibPpt().TimeNodeAudio_get_SoundName.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_get_SoundName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TimeNodeAudio_get_SoundName,self.Ptr))
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeNodeAudio_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeNodeAudio_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNodeAudio_Equals,self.Ptr, intPtrobj)
        return ret

