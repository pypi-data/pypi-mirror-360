from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OleObjectCollection (  ICollection, IEnumerable) :
    """
    <summary>
        A collection of OleObject controls.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets a number of objects in the collection.
    </summary>
        """
        GetDllLibPpt().OleObjectCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().OleObjectCollection_get_Count,self.Ptr)
        return ret


    def Remove(self ,item:'OleObject'):
        """
    <summary>
        Removes an OleObject control from the collection.
    </summary>
    <param name="item">A control to remove.</param>
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().OleObjectCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().OleObjectCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes an OleObject control stored at specified position from the collection.
    </summary>
    <param name="index">Index of a control to remove.</param>
        """
        
        GetDllLibPpt().OleObjectCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().OleObjectCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
    <summary>
        Removes all controls from the collection.
    </summary>
        """
        GetDllLibPpt().OleObjectCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().OleObjectCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'OleObject':
        """
    <summary>
        Gets a control at the specified position.
    </summary>
    <param name="index">Index of a control.</param>
        """
        
        GetDllLibPpt().OleObjectCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().OleObjectCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else OleObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().OleObjectCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies the entire collection to the specified array.
#    </summary>
#    <param name="array">Target array</param>
#    <param name="index">Index in the target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().OleObjectCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().OleObjectCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().OleObjectCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OleObjectCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().OleObjectCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


