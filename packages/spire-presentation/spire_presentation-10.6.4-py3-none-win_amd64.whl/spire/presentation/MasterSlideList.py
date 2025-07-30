from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MasterSlideList (SpireObject) :
    """
    <summary>
         Represents a collection of master slides.
     </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().MasterSlideList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MasterSlideList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().MasterSlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MasterSlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IMasterSlide(intPtr)
        return ret

    def get_Item(self ,index:int)->'IMasterSlide':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.MasterSlide" />.
    </summary>
        """
        
        GetDllLibPpt().MasterSlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MasterSlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IMasterSlide(intPtr)
        return ret



    def Remove(self ,value:'IMasterSlide'):
        """
    <summary>
        Removes the first occurrence of a specific object from the collection.
    </summary>
    <param name="value">The master slide to remove from the collection.</param>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().MasterSlideList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().MasterSlideList_Remove,self.Ptr, intPtrvalue)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the element at the specified index of the collection.
    </summary>
    <param name="index">The zero-based index of the element to remove.</param>
        """
        
        GetDllLibPpt().MasterSlideList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().MasterSlideList_RemoveAt,self.Ptr, index)

    def CleanupDesigns(self):
        """
    <summary>
        Removes unused master slides.
    </summary>
        """
        GetDllLibPpt().MasterSlideList_CleanupDesigns.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().MasterSlideList_CleanupDesigns,self.Ptr)


    def AppendSlide(self ,slide:'IMasterSlide')->int:
        """
    <summary>
        Adds a new master slide to the end of the collection.
    </summary>
    <returns>Index of new slide.</returns>
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().MasterSlideList_AppendSlide.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().MasterSlideList_AppendSlide.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MasterSlideList_AppendSlide,self.Ptr, intPtrslide)
        return ret


    def InsertSlide(self ,index:int,slide:'IMasterSlide'):
        """

        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().MasterSlideList_InsertSlide.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().MasterSlideList_InsertSlide,self.Ptr, index,intPtrslide)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().MasterSlideList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().MasterSlideList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterSlideList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


