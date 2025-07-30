from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartCategoryCollection (SpireObject) :
    """
    <summary>
        Represents collection of <see cref="T:Spire.Presentation.Charts.ChartCategory" /></summary>
    """

    def get_Item(self ,index:int)->'ChartCategory':
        """
    <summary>
        Gets the element at the specified index.
    </summary>
    <returns>
            The element at the specified index.
            </returns>
        """
        
        GetDllLibPpt().ChartCategoryCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartCategoryCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartCategoryCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartCategory(intPtr)
        return ret


    @property

    def CategoryLabels(self)->'CellRanges':
        """

        """
        GetDllLibPpt().ChartCategoryCollection_get_CategoryLabels.argtypes=[c_void_p]
        GetDllLibPpt().ChartCategoryCollection_get_CategoryLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartCategoryCollection_get_CategoryLabels,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @CategoryLabels.setter
    def CategoryLabels(self, value:'CellRanges'):
        GetDllLibPpt().ChartCategoryCollection_set_CategoryLabels.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_set_CategoryLabels,self.Ptr, value.Ptr)


    def AppendCellRange(self ,cellRange:'CellRange')->int:
        """
    <summary>
        Creates new chart category from <see cref="T:Spire.Presentation.Charts.CellRange" /> and adds it to the collection.
    </summary>
    <param name="cellRange">Cell to create chart category.</param>
    <returns>Index of new chart category.</returns>
        """
        intPtrcellRange:c_void_p = cellRange.Ptr

        GetDllLibPpt().ChartCategoryCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartCategoryCollection_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_Append,self.Ptr, intPtrcellRange)
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
        GetDllLibPpt().ChartCategoryCollection_AppendV.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartCategoryCollection_AppendV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_AppendV,self.Ptr,valuePtr)
        return ret


    def AppendFloat(self ,value:float)->int:
        """
    <summary>
        Append a numberic value.
    </summary>
    <param name="value"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().ChartCategoryCollection_AppendV1.argtypes=[c_void_p ,c_float]
        GetDllLibPpt().ChartCategoryCollection_AppendV1.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_AppendV1,self.Ptr, value)
        return ret

    def AppendSpireObject(self ,value:SpireObject)->int:
        """
    <summary>
         Creates new <see cref="T:Spire.Presentation.Charts.ChartCategory" /> from value and adds it to the collection.
    </summary>
    <param name="value">The value.</param>
    <returns>Index of a new added <see cref="T:Spire.Presentation.Charts.CellRange" />.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartCategoryCollection_AppendV11.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartCategoryCollection_AppendV11.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_AppendV11,self.Ptr, intPtrvalue)
        return ret


    def IndexOf(self ,value:'ChartCategory')->int:
        """
    <summary>
        Searches for the specified <see cref="T:Spire.Presentation.Charts.ChartCategory" /> and returns the zero-based index of the first occurrence within the entire Collection
    </summary>
    <param name="value">Chart category.</param>
    <returns>The zero-based index of the first occurrence of value within the entire CollectionBase, if found; otherwise, -1.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartCategoryCollection_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartCategoryCollection_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_IndexOf,self.Ptr, intPtrvalue)
        return ret


    def Remove(self ,value:'ChartCategory'):
        """
    <summary>
        Removes the specified value.
    </summary>
    <param name="value">The value.</param>
<exception cref="T:System.ArgumentException">The value parameter was not found in the collection.</exception>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartCategoryCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_Remove,self.Ptr, intPtrvalue)

    @property
    def Count(self)->int:
        """
        """

        GetDllLibPpt().ChartCategoryCollection_GetCount.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_GetCount,self.Ptr)
        return ret

    def Clear(self):
        """
        """

        GetDllLibPpt().ChartCategoryCollection_Clear.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_Clear,self.Ptr)

    @property
    def Capacity(self)->int:
        """
        """

        GetDllLibPpt().ChartCategoryCollection_getCapacity.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartCategoryCollection_getCapacity,self.Ptr)
        return ret
    
    @Capacity.setter
    def Capacity(self, value:int)->int:
        """
        """

        GetDllLibPpt().ChartCategoryCollection_setCapacity.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartCategoryCollection_setCapacity,self.Ptr,value)

