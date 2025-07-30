from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IAudioData (SpireObject) :
    """

    """
    @property

    def ContentType(self)->str:
        """
    <summary>
        Gets a MIME type of an audio.
    </summary>
        """
        GetDllLibPpt().IAudioData_get_ContentType.argtypes=[c_void_p]
        GetDllLibPpt().IAudioData_get_ContentType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAudioData_get_ContentType,self.Ptr))
        return ret


#    @property
#
#    def Data(self)->List['Byte']:
#        """
#    <summary>
#        Gets the copy of an audio's data.
#            Read-only <see cref="T:System.Byte" />[].
#    </summary>
#        """
#        GetDllLibPpt().IAudioData_get_Data.argtypes=[c_void_p]
#        GetDllLibPpt().IAudioData_get_Data.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().IAudioData_get_Data,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret


    @property

    def Stream(self)->'Stream':
        """
    <summary>
        Gets stream.
    </summary>
        """
        GetDllLibPpt().IAudioData_get_Stream.argtypes=[c_void_p]
        GetDllLibPpt().IAudioData_get_Stream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudioData_get_Stream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def GetStream(self)->'Stream':
        """
    <summary>
        Gets stream from audio.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().IAudioData_GetStream.argtypes=[c_void_p]
        GetDllLibPpt().IAudioData_GetStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudioData_GetStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveToFile(self ,fileName:str):
        """
    <summary>
        Save audio to disk.
    </summary>
    <param name="fileName"></param>
        """
        
        fileNamePtr = StrToPtr(fileName)
        GetDllLibPpt().IAudioData_SaveToFile.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IAudioData_SaveToFile,self.Ptr,fileNamePtr)

