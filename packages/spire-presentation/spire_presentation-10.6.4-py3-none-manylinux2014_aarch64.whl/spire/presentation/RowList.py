from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class RowList (  SpireObject ) :
    """
    <summary>
        Represents a collection of rows.
    </summary>
    """
    @dispatch
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().RowList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().RowList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RowList_get_Item,self.Ptr, key)
        ret = None if intPtr==None else TableRow(intPtr)
        return ret

    def get_Item(self ,index:int)->'TableRow':
        """
    <summary>
        Gets the element at the specified index.
    </summary>
        """
        
        GetDllLibPpt().RowList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().RowList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RowList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TableRow(intPtr)
        return ret



    def Append(self ,row:'TableRow')->int:
        """
    <summary>
        Add new row.
    </summary>
    <param name="row"></param>
    <returns></returns>
        """
        intPtrrow:c_void_p = row.Ptr

        GetDllLibPpt().RowList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().RowList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().RowList_Append,self.Ptr, intPtrrow)
        return ret


    def Insert(self ,index:int,row:'TableRow'):
        """
    <summary>
        Insert a row.
    </summary>
    <param name="index"></param>
    <param name="row"></param>
        """
        intPtrrow:c_void_p = row.Ptr

        GetDllLibPpt().RowList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().RowList_Insert,self.Ptr, index,intPtrrow)


    def RemoveAt(self ,firstRowIndex:int,withAttachedRows:bool):
        """
    <summary>
        Removes a row at the specified position from a table.
    </summary>
    <param name="firstRowIndex">Index of a row to delete.</param>
    <param name="withAttachedRows">True to delete also all attached rows.</param>
        """
        
        GetDllLibPpt().RowList_RemoveAt.argtypes=[c_void_p ,c_int,c_bool]
        CallCFunction(GetDllLibPpt().RowList_RemoveAt,self.Ptr, firstRowIndex,withAttachedRows)

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
    </summary>
        """
        GetDllLibPpt().RowList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().RowList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().RowList_get_Count,self.Ptr)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().RowList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().RowList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RowList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


