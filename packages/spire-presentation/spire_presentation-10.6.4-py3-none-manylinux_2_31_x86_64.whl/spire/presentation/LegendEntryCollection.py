from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LegendEntryCollection (SpireObject) :
    """
    <summary>
        Represents collection of  <see cref="T:Spire.Presentation.Charts.ChartSeriesDataFormat" /></summary>
    """

    def get_Item(self ,index:int)->'LegendEntry':
        """
    <summary>
        Gets the element at the specified index.
    </summary>
    <returns>
            The element at the specified index.
              </returns>
        """
        
        GetDllLibPpt().LegendEntryCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().LegendEntryCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LegendEntryCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else LegendEntry(intPtr)
        return ret
    

    @property
    def Count(self)->int:
        """
        """
        
        GetDllLibPpt().LegendEntryCollection_GetCount.argtypes=[c_void_p]
        GetDllLibPpt().LegendEntryCollection_GetCount.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LegendEntryCollection_GetCount,self.Ptr)
        return ret


