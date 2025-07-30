from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStopList ( IActiveSlide) :
    """
    <summary>
        Represnts a collection of gradient stops.
    </summary>
    """

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().GradientStopList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().GradientStopList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else GradientStop(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of gradient stops in a collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().GradientStopList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'GradientStop':
        """
    <summary>
        Gets the gradient stop by index.
    </summary>
        """
        
        GetDllLibPpt().GradientStopList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().GradientStopList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else GradientStop(intPtr)
        return ret


    def AppendByColor(self ,position:float,color:Color)->int:
        """
    <summary>
        Creates the new gradient stop.
    </summary>
    <param name="position">Position of the new gradient stop.</param>
    <param name="color">Color of the new radient stop.</param>
    <returns>Index of the new gradient stop in the collection.</returns>
        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibPpt().GradientStopList_Append.argtypes=[c_void_p ,c_float,c_void_p]
        GetDllLibPpt().GradientStopList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_Append,self.Ptr, position,intPtrcolor)
        return ret

    def AppendByKnownColors(self ,position:float,knownColor:KnownColors)->int:
        """
    <summary>
        Creates the new gradient stop and adds it to the collection.
    </summary>
    <param name="position">Position of the new gradient stop.</param>
    <param name="knownColor">Color of the new radient stop.</param>
    <returns>Index of the new gradient stop in the collection.</returns>
        """
        enumknownColor:c_int = knownColor.value

        GetDllLibPpt().GradientStopList_AppendPK.argtypes=[c_void_p ,c_float,c_int]
        GetDllLibPpt().GradientStopList_AppendPK.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_AppendPK,self.Ptr, position,enumknownColor)
        return ret


    def AppendBySchemeColor(self ,position:float,schemeColor:SchemeColor)->int:
        """
    <summary>
        Creates the new gradient stop.
    </summary>
    <param name="position">Position of the new gradient stop.</param>
    <param name="schemeColor">Color of the new radient stop.</param>
    <returns>Index of the new gradient stop in the collection.</returns>
        """
        enumschemeColor:c_int = schemeColor.value

        GetDllLibPpt().GradientStopList_AppendPS.argtypes=[c_void_p ,c_float,c_int]
        GetDllLibPpt().GradientStopList_AppendPS.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_AppendPS,self.Ptr, position,enumschemeColor)
        return ret

  
    def InsertByColor(self ,index:int,position:float,color:Color):
        """
    <summary>
        Creates the new gradient stop.
    </summary>
    <param name="index">Index in the collection where new gradient stop will be inserted.</param>
    <param name="position">Position of the new gradient stop.</param>
    <param name="color">Color of the new radient stop.</param>
        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibPpt().GradientStopList_Insert.argtypes=[c_void_p ,c_int,c_float,c_void_p]
        CallCFunction(GetDllLibPpt().GradientStopList_Insert,self.Ptr, index,position,intPtrcolor)

   
    def InsertByKnownColors(self ,index:int,position:float,knownColor:KnownColors):
        """
    <summary>
        Creates the new gradient stop.
    </summary>
    <param name="index">Index in the collection where new gradient stop will be inserted.</param>
    <param name="position">Position of the new gradient stop.</param>
    <param name="knownColor">Color of the new radient stop.</param>
        """
        enumknownColor:c_int = knownColor.value

        GetDllLibPpt().GradientStopList_InsertIPK.argtypes=[c_void_p ,c_int,c_float,c_int]
        CallCFunction(GetDllLibPpt().GradientStopList_InsertIPK,self.Ptr, index,position,enumknownColor)

    
    def InsertBySchemeColor(self ,index:int,position:float,schemeColor:SchemeColor):
        """
    <summary>
        Creates the new gradient stop.
    </summary>
    <param name="index">Index in the collection where new gradient stop will be inserted.</param>
    <param name="position">Position of the new gradient stop.</param>
    <param name="schemeColor">Color of the new radient stop.</param>
        """
        enumschemeColor:c_int = schemeColor.value

        GetDllLibPpt().GradientStopList_InsertIPS.argtypes=[c_void_p ,c_int,c_float,c_int]
        CallCFunction(GetDllLibPpt().GradientStopList_InsertIPS,self.Ptr, index,position,enumschemeColor)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes a gradient stop at the specified index.
    </summary>
    <param name="index">Index of a gradient stop that should be deleted.</param>
        """
        
        GetDllLibPpt().GradientStopList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().GradientStopList_RemoveAt,self.Ptr, index)

    def RemoveAll(self):
        """
    <summary>
        Removes all gradient stops from a collection.
    </summary>
        """
        GetDllLibPpt().GradientStopList_RemoveAll.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().GradientStopList_RemoveAll,self.Ptr)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().GradientStopList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


