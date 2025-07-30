from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAnimationCollection (  SpireObject ) :
    """
    <summary>
        Represent collection of text animations.
    </summary>
    """
    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().TextAnimationCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextAnimationCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextAnimation(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
    <summary>
        Gets a number of elements in the collection.
    </summary>
        """
        GetDllLibPpt().TextAnimationCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_Count,self.Ptr)
        return ret

    @dispatch

    def get_Item(self ,index:int)->TextAnimation:
        """
    <summary>
        Gets element by index.
    </summary>
        """
        
        GetDllLibPpt().TextAnimationCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextAnimationCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextAnimation(intPtr)
        return ret


#    @dispatch
#
#    def get_Item(self ,shape:IShape)->List[TextAnimation]:
#        """
#    <summary>
#        Gets all elements 
#    </summary>
#    <param name="shape"></param>
#    <returns></returns>
#        """
#        intPtrshape:c_void_p = shape.Ptr
#
#        GetDllLibPpt().TextAnimationCollection_get_ItemS.argtypes=[c_void_p ,c_void_p]
#        GetDllLibPpt().TextAnimationCollection_get_ItemS.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_ItemS,self.Ptr, intPtrshape)
#        ret = GetObjVectorFromArray(intPtrArray, TextAnimation)
#        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextAnimationCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextAnimationCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextAnimationCollection_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an iterator for a collection.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().TextAnimationCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
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
#        GetDllLibPpt().TextAnimationCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().TextAnimationCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().TextAnimationCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().TextAnimationCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


