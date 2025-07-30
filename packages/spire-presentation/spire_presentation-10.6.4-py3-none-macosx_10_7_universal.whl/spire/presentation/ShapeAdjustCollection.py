from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAdjustCollection (  ShapeAdjustmentList, ICollection, IEnumerable) :
    """
    <summary>
        Reprasents a collection of shape's adjustments.
    </summary>
    """
#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements from the collection to the specified array.
#    </summary>
#    <param name="array">Target array.</param>
#    <param name="index">Starting index in the target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().ShapeAdjustCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().ShapeAdjustCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().ShapeAdjustCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeAdjustCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().ShapeAdjustCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeAdjustCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
        """
        GetDllLibPpt().ShapeAdjustCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeAdjustCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


