from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CellCollection (  PptObject, IActiveSlide) :
    """
    <summary>
        Represents a collection of cells.
    </summary>
    """

    @dispatch
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().CellCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Item,self.Ptr, key)
        ret = None if intPtr==None else Cell(intPtr)
        return ret

    def get_Item(self ,index:int)->'Cell':
        """
    <summary>
        Gets a cell by index.
            Read-only <see cref="T:Spire.Presentation.Cell" />.
    </summary>
        """
        
        GetDllLibPpt().CellCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Cell(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
    <summary>
        Gets the count of cells in a collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().CellCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellCollection_get_Count,self.Ptr)
        return ret

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a CellExCollection.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().CellCollection_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
    <summary>
        Gets the parent presentation of a CellExCollection.
            Read-only <see cref="T:Spire.Presentation.PresentationPptx" />.
    </summary>
        """
        GetDllLibPpt().CellCollection_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for all cells which top-left corner
            belongs to this collection. Each cell returned only once.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the collection.</returns>
        """
        GetDllLibPpt().CellCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_GetEnumerator,self.Ptr)
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
#        GetDllLibPpt().CellCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().CellCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().CellCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CellCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().CellCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().CellCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


