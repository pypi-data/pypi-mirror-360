from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ChartDataPointCollection (  IEnumerable) :
    """
    <summary>
        Represents a collection of ChartPoint.
    </summary>
    """

    def get_Item(self ,index:int)->'ChartDataPoint':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.Charts.ChartDataPoint" />.
    </summary>
        """
        
        GetDllLibPpt().ChartDataPointCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartDataPointCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPointCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartDataPoint(intPtr)
        return ret



    def Add(self ,value:'ChartDataPoint')->int:
        """
    <summary>
        Adds the new DataLabel at the end of a collection.
    </summary>
    <param name="value">The DataLabel </param>
    <returns></returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartDataPointCollection_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartDataPointCollection_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPointCollection_Add,self.Ptr, intPtrvalue)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
        """
        GetDllLibPpt().ChartDataPointCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPointCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPointCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartDataPointCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPointCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPointCollection_get_Count,self.Ptr)
        return ret

