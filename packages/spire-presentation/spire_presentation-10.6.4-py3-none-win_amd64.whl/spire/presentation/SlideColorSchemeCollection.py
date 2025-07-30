from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideColorSchemeCollection (  ICollection, IEnumerable) :
    """
    <summary>
        Represents a collection of additional color schemes.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets a number of elements int the collection.
            Readonly <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().SlideColorSchemeCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'SlideColorScheme':
        """
    <summary>
        Gets an color scheme by index.
            Readonly <see cref="T:Spire.Presentation.SlideColorScheme" />.
    </summary>
        """
        
        GetDllLibPpt().SlideColorSchemeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideColorSchemeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else SlideColorScheme(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SlideColorSchemeCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator, which can be used to iterate through the collection.
    </summary>
    <returns>Enumeraton <see cref="T:System.Collections.IEnumerator" />.</returns>
        """
        GetDllLibPpt().SlideColorSchemeCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements of the collection to the specified array.
#    </summary>
#    <param name="array">Target array.</param>
#    <param name="index">Starting index in the array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().SlideColorSchemeCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the ArrayList is synchronized (thread safe).
            Readonly <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().SlideColorSchemeCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets an object that can be used to synchronize access to the collection.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().SlideColorSchemeCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


