from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class _Presentation (  PptObject) :
    """
    <summary>
        Represents an Presentation document. 
    </summary>
    """
#
#    def GetBytes(self)->List['Byte']:
#        """
#
#        """
#        GetDllLibPpt()._Presentation_GetBytes.argtypes=[c_void_p]
#        GetDllLibPpt()._Presentation_GetBytes.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt()._Presentation_GetBytes,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret



    def GetStream(self)->'Stream':
        """

        """
        GetDllLibPpt()._Presentation_GetStream.argtypes=[c_void_p]
        GetDllLibPpt()._Presentation_GetStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt()._Presentation_GetStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat):
        """

        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt()._Presentation_LoadFromStream.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromStream,self.Ptr, intPtrstream,enumfileFormat)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat):
        """

        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt()._Presentation_LoadFromFile.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFile,self.Ptr,filePtr,enumfileFormat)

    @dispatch

    def LoadFromFile(self ,file:str):
        """

        """
        
        filePtr = StrToPtr(file)
        GetDllLibPpt()._Presentation_LoadFromFileF.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFileF,self.Ptr,filePtr)

    @dispatch

    def LoadFromFile(self ,file:str,password:str):
        """

        """
        
        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt()._Presentation_LoadFromFileFP.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFileFP,self.Ptr,filePtr,passwordPtr)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat,password:str):
        """

        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt()._Presentation_LoadFromFileFFP.argtypes=[c_void_p ,c_char_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFileFFP,self.Ptr,filePtr,enumfileFormat,passwordPtr)

    @dispatch

    def SaveToFile(self ,stream:Stream,fileFormat:FileFormat):
        """

        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt()._Presentation_SaveToFile.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_SaveToFile,self.Ptr, intPtrstream,enumfileFormat)

    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat,password:str):
        """
    <summary>
        Opens the document from a stream.
    </summary>
    <param name="stream">The document stream.</param>
    <param name="fileFormat">The file format</param>
    <param name="password">The password.</param>
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        passwordPtr = StrToPtr(password)
        GetDllLibPpt()._Presentation_LoadFromStreamSFP.argtypes=[c_void_p ,c_void_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromStreamSFP,self.Ptr, intPtrstream,enumfileFormat,passwordPtr)

    @dispatch

    def SaveToFile(self ,file:str,fileFormat:FileFormat):
        """

        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt()._Presentation_SaveToFileFF.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_SaveToFileFF,self.Ptr,filePtr,enumfileFormat)

