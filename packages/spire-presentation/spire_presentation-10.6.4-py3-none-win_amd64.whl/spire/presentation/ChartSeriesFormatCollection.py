from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartSeriesFormatCollection (SpireObject) :
    """
    <summary>
        Represents collection of  <see cref="T:Spire.Presentation.Charts.ChartSeriesDataFormat" /></summary>
    """
    @property

    def SeriesLabel(self)->'CellRanges':
        """
    <summary>
        Gets or sets chart series value.
    </summary>
        """
        GetDllLibPpt().ChartSeriesFormatCollection_get_SeriesLabel.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_get_SeriesLabel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_SeriesLabel,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @SeriesLabel.setter
    def SeriesLabel(self, value:'CellRanges'):
        GetDllLibPpt().ChartSeriesFormatCollection_set_SeriesLabel.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_set_SeriesLabel,self.Ptr, value.Ptr)


    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartSeriesDataFormat(intPtr)
        return ret

    def get_Item(self ,index:int)->'ChartSeriesDataFormat':
        """
    <summary>
        Gets the element at the specified index.
    </summary>
    <returns>
            The element at the specified index.
              </returns>
        """
        
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartSeriesFormatCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartSeriesDataFormat(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesFormatCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_Count,self.Ptr)
        return ret

    
    def AppendCellRange(self ,cellRange:'CellRange')->int:
        """

        """
        
        intPtrcellRange:c_void_p = cellRange.Ptr
        
        GetDllLibPpt().ChartSeriesFormatCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_Append,self.Ptr, intPtrcellRange)
        return ret


    def AppendStr(self ,value:str)->int:
        """
    <summary>
        Append a string value.
    </summary>
    <param name="value"></param>
    <returns></returns>
        """
        
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_AppendV,self.Ptr,valuePtr)
        return ret


    def AppendFloat(self ,value:float)->int:
        """
    <summary>
        Append a numberic value.
    </summary>
    <param name="value"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV1.argtypes=[c_void_p ,c_float]
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV1.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_AppendV1,self.Ptr, value)
        return ret


    def AppendSpireObject(self ,value:SpireObject)->int:
        """
    <summary>
        Append a value;
    </summary>
    <param name="value"></param>
    <returns></returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartSeriesFormatCollection_AppendV11.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_AppendV11.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_AppendV11,self.Ptr, intPtrvalue)
        return ret


    def IndexOf(self ,value:'ChartSeriesDataFormat')->int:
        """
    <summary>
        Searches for the specified <see cref="T:Spire.Presentation.Charts.ChartSeriesDataFormat" /> and returns the zero-based index of the first occurrence within the entire Collection
    </summary>
    <param name="value">Chart series value.</param>
    <returns>The zero-based index of the first occurrence of value within the entire CollectionBase, if found; otherwise, -1.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartSeriesFormatCollection_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_IndexOf,self.Ptr, intPtrvalue)
        return ret


    def Remove(self ,value:'ChartSeriesDataFormat'):
        """
    <summary>
        Removes the specified value.
    </summary>
    <param name="value">The value.</param>
<exception cref="T:System.ArgumentException">The value parameter was not found in the collection.</exception>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartSeriesFormatCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_Remove,self.Ptr, intPtrvalue)

    def RemoveAt(self ,value:'int'):
        """
        """
        intPtrvalue:c_void_p = value

        GetDllLibPpt().ChartSeriesFormatCollection_RemoveAt.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_RemoveAt,self.Ptr, intPtrvalue)

    def Clear(self):
        """
        """

        GetDllLibPpt().ChartSeriesFormatCollection_clear.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_clear,self.Ptr)

    @property
    def KeepSeriesFormat(self)->bool:
        """
    <summary>
        Get or set whether change series format when reset the SeriesLabel.
    </summary>
        """
        GetDllLibPpt().ChartSeriesFormatCollection_get_KeepSeriesFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesFormatCollection_get_KeepSeriesFormat.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_get_KeepSeriesFormat,self.Ptr)
        return ret

    @KeepSeriesFormat.setter
    def KeepSeriesFormat(self, value:bool):
        GetDllLibPpt().ChartSeriesFormatCollection_set_KeepSeriesFormat.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_set_KeepSeriesFormat,self.Ptr, value)

    @property
    def Capacity(self)->int:
        """
        """

        GetDllLibPpt().ChartSeriesFormatCollection_getCapacity.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_getCapacity,self.Ptr)
        return ret
    
    @Capacity.setter
    def Capacity(self, value:int)->int:
        """
        """

        GetDllLibPpt().ChartSeriesFormatCollection_setCapacity.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesFormatCollection_setCapacity,self.Ptr,value)

