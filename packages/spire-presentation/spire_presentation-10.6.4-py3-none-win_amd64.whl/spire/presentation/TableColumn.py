from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableColumn (  CellCollection) :
    """
    <summary>
        Represents a table column.
    </summary>
    """
    @property
    def Width(self)->float:
        """
    <summary>
        Gets or sets the width of a column.
            Read/Write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().TableColumn_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().TableColumn_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TableColumn_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().TableColumn_set_Width.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().TableColumn_set_Width,self.Ptr, value)

