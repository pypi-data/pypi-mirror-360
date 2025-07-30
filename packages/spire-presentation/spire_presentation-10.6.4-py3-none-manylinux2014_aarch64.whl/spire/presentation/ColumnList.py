from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColumnList (  SpireObject) :
    """
    <summary>
        Represents collection of columns in a table.
    </summary>
    """

    @dispatch
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().ColumnList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ColumnList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColumnList_get_Item,self.Ptr, key)
        ret = None if intPtr==None else TableColumn(intPtr)
        return ret

    def get_Item(self ,index:int)->'TableColumn':
        """
    <summary>
        Gets the column at the specified index.
            Read-only <see cref="T:Spire.Presentation.TableColumn" />.
    </summary>
        """
        
        GetDllLibPpt().ColumnList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ColumnList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColumnList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TableColumn(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of columns in a collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ColumnList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ColumnList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColumnList_get_Count,self.Ptr)
        return ret


    def Insert(self ,index:int,template:'TableColumn'):
        """
    <summary>
        Insert column in a table.
    </summary>
    <param name="index"></param>
    <param name="template"></param>
        """
        intPtrtemplate:c_void_p = template.Ptr

        GetDllLibPpt().ColumnList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ColumnList_Insert,self.Ptr, index,intPtrtemplate)


    def Add(self ,template:'TableColumn'):
        """
    <summary>
        Insert column in a table.
    </summary>
    <param name="template"></param>
        """
        intPtrtemplate:c_void_p = template.Ptr

        GetDllLibPpt().ColumnList_Add.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ColumnList_Add,self.Ptr, intPtrtemplate)


    def RemoveAt(self ,firstColumnIndex:int,withAttachedRows:bool):
        """
    <summary>
        Removes a column at the specified position from a table.
    </summary>
    <param name="firstColumnIndex">Index of a column to delete.</param>
    <param name="withAttachedRows">True to delete also all attached columns.</param>
        """
        
        GetDllLibPpt().ColumnList_RemoveAt.argtypes=[c_void_p ,c_int,c_bool]
        CallCFunction(GetDllLibPpt().ColumnList_RemoveAt,self.Ptr, firstColumnIndex,withAttachedRows)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().ColumnList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ColumnList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColumnList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


