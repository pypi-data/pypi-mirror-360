from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class UOPWriter (SpireObject) :
    """

    """
    @staticmethod

    def OoxToUof(ooxFileName:str,uosFileName:str):
        """

        """
        
        ooxFileNamePtr = StrToPtr(ooxFileName)
        uosFileNamePtr = StrToPtr(uosFileName)
        GetDllLibPpt().UOPWriter_OoxToUof.argtypes=[ c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().UOPWriter_OoxToUof,ooxFileNamePtr,uosFileNamePtr)

