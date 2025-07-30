from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectStyleCollection (  EffectStyleList, ICollection) :
    """
    <summary>
        Represents a collection of effect styles.
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectStyleCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectStyleCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyleCollection_Equals,self.Ptr, intPtrobj)
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
#        GetDllLibPpt().EffectStyleCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().EffectStyleCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().EffectStyleCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyleCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().EffectStyleCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyleCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


