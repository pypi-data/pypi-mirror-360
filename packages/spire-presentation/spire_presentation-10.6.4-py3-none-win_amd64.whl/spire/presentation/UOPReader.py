from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class UOPReader (SpireObject) :
    """

    """
    @staticmethod

    def UofToOox(uosFileName:str,ooxFileName:str):
        """

        """
        
        uosFileNamePtr = StrToPtr(uosFileName)
        ooxFileNamePtr = StrToPtr(ooxFileName)
        GetDllLibPpt().UOPReader_UofToOox.argtypes=[ c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().UOPReader_UofToOox,uosFileNamePtr,ooxFileNamePtr)

