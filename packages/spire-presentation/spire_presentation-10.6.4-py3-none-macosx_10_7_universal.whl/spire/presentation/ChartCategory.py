from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartCategory (  PptObject) :
    """
    <summary>
        Represents chart categories.
    </summary>
    """
    @property

    def DataRange(self)->'CellRange':
        """
    <summary>
        Gets or sets Spire.Xls.Cell object.
    </summary>
        """
        GetDllLibPpt().ChartCategory_get_DataRange.argtypes=[c_void_p]
        GetDllLibPpt().ChartCategory_get_DataRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartCategory_get_DataRange,self.Ptr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @DataRange.setter
    def DataRange(self, value:'CellRange'):
        GetDllLibPpt().ChartCategory_set_DataRange.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategory_set_DataRange,self.Ptr, value.Ptr)

