from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MasterSlideCollection (  MasterSlideList) :
    """
    <summary>
        Represents a collection of master slides.
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
#        GetDllLibPpt().MasterSlideCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().MasterSlideCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().MasterSlideCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().MasterSlideCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().MasterSlideCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


