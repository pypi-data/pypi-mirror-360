from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SaveToPptxOption (SpireObject) :
    """
    <summary>
        Save to pptx option
    </summary>
    """
    @property
    def SaveToWPS(self)->bool:
        """
    <summary>
        Get or set if save to wps office.
    </summary>
        """
        GetDllLibPpt().SaveToPptxOption_get_SaveToWPS.argtypes=[c_void_p]
        GetDllLibPpt().SaveToPptxOption_get_SaveToWPS.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SaveToPptxOption_get_SaveToWPS,self.Ptr)
        return ret

    @SaveToWPS.setter
    def SaveToWPS(self, value:bool):
        GetDllLibPpt().SaveToPptxOption_set_SaveToWPS.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SaveToPptxOption_set_SaveToWPS,self.Ptr, value)

