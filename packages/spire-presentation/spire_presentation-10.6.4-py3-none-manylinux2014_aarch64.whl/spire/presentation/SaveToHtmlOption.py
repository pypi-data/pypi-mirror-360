from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SaveToHtmlOption (SpireObject) :
    """
    <summary>
        save to html option.
    </summary>
    """
    @property
    def Center(self)->bool:
        """
    <summary>
        Get or set if save to html align center.
    </summary>
        """
        GetDllLibPpt().SaveToHtmlOption_get_Center.argtypes=[c_void_p]
        GetDllLibPpt().SaveToHtmlOption_get_Center.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SaveToHtmlOption_get_Center,self.Ptr)
        return ret

    @Center.setter
    def Center(self, value:bool):
        GetDllLibPpt().SaveToHtmlOption_set_Center.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SaveToHtmlOption_set_Center,self.Ptr, value)

