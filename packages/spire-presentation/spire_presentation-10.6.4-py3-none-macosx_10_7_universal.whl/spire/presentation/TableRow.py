from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableRow (  CellCollection) :
    """
    <summary>
        Represents a row in a table.
    </summary>
    """
    @property
    def Height(self)->float:
        """
    <summary>
        Gets the height of a row.
            Read-only <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().TableRow_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().TableRow_get_Height.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TableRow_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().TableRow_set_Height.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().TableRow_set_Height,self.Ptr, value)

