from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TagCollection (TagList) :
    """
    <summary>
        Represents the collection of tags (user defined pairs of strings)
    </summary>
    """
#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements from the collection into the specified array.
#    </summary>
#    <param name="array">Array to fill.</param>
#    <param name="index">Starting position in target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().TagCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().TagCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().TagCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().TagCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TagCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().TagCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().TagCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TagCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
        """
        GetDllLibPpt().TagCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TagCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TagCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


