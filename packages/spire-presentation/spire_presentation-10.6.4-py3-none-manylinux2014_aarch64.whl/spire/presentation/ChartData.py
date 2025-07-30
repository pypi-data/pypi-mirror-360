from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartData (SpireObject) :
    """
    <summary>
        Chart data.
    </summary>
    """

    @dispatch
    def __getitem__(self, row,column):
        
        GetDllLibPpt().ChartData_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ChartData_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_Item,self.Ptr, row,column)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    @dispatch
    def __getitem__(self, startRow,startColumn,endRow,endColumn):
        
        GetDllLibPpt().ChartData_get_ItemRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibPpt().ChartData_get_ItemRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemRCLL,self.Ptr, startRow,startColumn,endRow,endColumn)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret

    @dispatch
    def __getitem__(self, name:str):
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().ChartData_get_ItemN.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartData_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemN,self.Ptr,namePtr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    @dispatch

    def get_Item(self ,row:int,column:int)->CellRange:
        """
    <summary>
        Get cell range.
    </summary>
    <param name="row"></param>
    <param name="column"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().ChartData_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ChartData_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_Item,self.Ptr, row,column)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret



    def Clear(self ,row:int,column:int,lastRow:int,lastColumn:int):
        """
    <summary>
        clear data.
    </summary>
    <param name="row"></param>
    <param name="column"></param>
    <param name="lastRow"></param>
    <param name="lastColumn"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().ChartData_Clear.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibPpt().ChartData_Clear,self.Ptr, row,column,lastRow,lastColumn)

    @dispatch

    def get_Item(self ,row:int,column:int,lastRow:int,lastColumn:int)->CellRanges:
        """
    <summary>
        Get cell ranges.
    </summary>
    <param name="row"></param>
    <param name="column"></param>
    <param name="lastRow"></param>
    <param name="lastColumn"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().ChartData_get_ItemRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int]
        GetDllLibPpt().ChartData_get_ItemRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemRCLL,self.Ptr, row,column,lastRow,lastColumn)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @dispatch

    def get_Item(self ,worksheetIndex:int,row:int,column:int,lastRow:int,lastColumn:int)->CellRanges:
        """
    <summary>
        Get cell ranges.
    </summary>
    <param name="worksheetIndex"></param>
    <param name="row"></param>
    <param name="column"></param>
    <param name="lastRow"></param>
    <param name="lastColumn"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().ChartData_get_ItemWRCLL.argtypes=[c_void_p ,c_int,c_int,c_int,c_int,c_int]
        GetDllLibPpt().ChartData_get_ItemWRCLL.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemWRCLL,self.Ptr, worksheetIndex,row,column,lastRow,lastColumn)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str)->CellRange:
        """
    <summary>
        Get cell range.
    </summary>
    <param name="name"></param>
    <returns></returns>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().ChartData_get_ItemN.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ChartData_get_ItemN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemN,self.Ptr,namePtr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,name:str,endCellName:str)->CellRanges:
        """
    <summary>
        Get cell range.
    </summary>
    <param name="name"></param>
    <returns></returns>
        """
        
        namePtr = StrToPtr(name)
        endCellNamePtr = StrToPtr(endCellName)
        GetDllLibPpt().ChartData_get_ItemNE.argtypes=[c_void_p ,c_char_p,c_char_p]
        GetDllLibPpt().ChartData_get_ItemNE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemNE,self.Ptr,namePtr,endCellNamePtr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @dispatch

    def get_Item(self ,worksheetIndex:int,name:str)->CellRange:
        """
    <summary>
        Get cell range.
    </summary>
    <param name="name"></param>
    <returns></returns>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().ChartData_get_ItemWN.argtypes=[c_void_p ,c_int,c_char_p]
        GetDllLibPpt().ChartData_get_ItemWN.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemWN,self.Ptr, worksheetIndex,namePtr)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret


    @dispatch

    def get_Item(self ,worksheetIndex:int,name:str,endCellName:str)->CellRanges:
        """
    <summary>
        Get cell range.
    </summary>
    <param name="name"></param>
    <returns></returns>
        """
        
        namePtr = StrToPtr(name)
        endCellNamePtr = StrToPtr(endCellName)
        GetDllLibPpt().ChartData_get_ItemWNE.argtypes=[c_void_p ,c_int,c_char_p,c_char_p]
        GetDllLibPpt().ChartData_get_ItemWNE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartData_get_ItemWNE,self.Ptr, worksheetIndex,namePtr,endCellNamePtr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret
    

    @property
    def LastRowIndex(self)->int:
        """
        """

        GetDllLibPpt().ChartData_LastRowIndex.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartData_LastRowIndex,self.Ptr)
        return ret
    
    @property
    def LastColIndex(self)->int:
        """
        """

        GetDllLibPpt().ChartData_LastColIndex.argtypes=[c_void_p ,c_void_p]
        ret = CallCFunction(GetDllLibPpt().ChartData_LastColIndex,self.Ptr)
        return ret


