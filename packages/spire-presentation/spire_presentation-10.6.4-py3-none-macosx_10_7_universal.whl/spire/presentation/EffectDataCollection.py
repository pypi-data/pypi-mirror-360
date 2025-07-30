from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectDataCollection (  ICollection, IEnumerable) :
    """
    <summary>
        Represents a readonly collection of EffectData objects.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of image effects in a collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().EffectDataCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().EffectDataCollection_get_Count,self.Ptr)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().EffectDataCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDataCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def get_Item(self ,index:int)->'EffectNode':
        """
    <summary>
        Gets element by index.
    </summary>
    <param name="index"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().EffectDataCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EffectDataCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDataCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else EffectNode(intPtr)
        return ret


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
#        GetDllLibPpt().EffectDataCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().EffectDataCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().EffectDataCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectDataCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().EffectDataCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().EffectDataCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDataCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


