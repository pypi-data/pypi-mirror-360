from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IDigitalSignature (SpireObject) :
    """
    <summary>
        Represents a DigitalSignature in Presentation.
    </summary>
    """
#    @property
#
#    def Certificate(self)->'X509Certificate2':
#        """
#    <summary>
#        Certificate object that was used to sign.
#    </summary>
#        """
#        GetDllLibPpt().IDigitalSignature_get_Certificate.argtypes=[c_void_p]
#        GetDllLibPpt().IDigitalSignature_get_Certificate.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().IDigitalSignature_get_Certificate,self.Ptr)
#        ret = None if intPtr==None else X509Certificate2(intPtr)
#        return ret
#


#    @Certificate.setter
#    def Certificate(self, value:'X509Certificate2'):
#        GetDllLibPpt().IDigitalSignature_set_Certificate.argtypes=[c_void_p, c_void_p]
#        CallCFunction(GetDllLibPpt().IDigitalSignature_set_Certificate,self.Ptr, value.Ptr)


    @property

    def Comments(self)->str:
        """
    <summary>
        Signature Comments.
    </summary>
        """
        GetDllLibPpt().IDigitalSignature_get_Comments.argtypes=[c_void_p]
        GetDllLibPpt().IDigitalSignature_get_Comments.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDigitalSignature_get_Comments,self.Ptr))
        return ret


    @Comments.setter
    def Comments(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDigitalSignature_set_Comments.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDigitalSignature_set_Comments,self.Ptr,valuePtr)

    @property

    def SignTime(self)->'DateTime':
        """
    <summary>
        Sign Time.
    </summary>
        """
        GetDllLibPpt().IDigitalSignature_get_SignTime.argtypes=[c_void_p]
        GetDllLibPpt().IDigitalSignature_get_SignTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IDigitalSignature_get_SignTime,self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @SignTime.setter
    def SignTime(self, value:'DateTime'):
        GetDllLibPpt().IDigitalSignature_set_SignTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IDigitalSignature_set_SignTime,self.Ptr, value.Ptr)

    @property
    def IsValid(self)->bool:
        """
    <summary>
        Indicates whether this digital signature is valid.
    </summary>
        """
        GetDllLibPpt().IDigitalSignature_get_IsValid.argtypes=[c_void_p]
        GetDllLibPpt().IDigitalSignature_get_IsValid.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IDigitalSignature_get_IsValid,self.Ptr)
        return ret

    @IsValid.setter
    def IsValid(self, value:bool):
        GetDllLibPpt().IDigitalSignature_set_IsValid.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IDigitalSignature_set_IsValid,self.Ptr, value)

