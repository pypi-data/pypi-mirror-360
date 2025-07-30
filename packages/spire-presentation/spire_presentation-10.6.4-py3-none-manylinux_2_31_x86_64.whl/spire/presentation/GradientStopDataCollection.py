from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStopDataCollection (  ICollection, IEnumerable) :
    """
    <summary>
        Represents a collection of GradientStopData objects.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of gradient stops in a collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().GradientStopDataCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'GradientStopData':
        """
    <summary>
        Gets the gradient stop by index.
    </summary>
        """
        
        GetDllLibPpt().GradientStopDataCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().GradientStopDataCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else GradientStopData(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().GradientStopDataCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopDataCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


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
#        GetDllLibPpt().GradientStopDataCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().GradientStopDataCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().GradientStopDataCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().GradientStopDataCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopDataCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopDataCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


