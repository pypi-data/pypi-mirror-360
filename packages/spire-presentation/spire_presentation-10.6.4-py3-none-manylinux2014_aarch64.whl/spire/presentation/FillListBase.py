from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillListBase (  IEnumerable) :
    """
    <summary>
        Represents a collection of FillFormat objects.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
    </summary>
        """
        GetDllLibPpt().FillListBase_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().FillListBase_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillListBase_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'FillFormat':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        
        GetDllLibPpt().FillListBase_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().FillListBase_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillListBase_get_Item,self.Ptr, index)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillListBase_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillListBase_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillListBase_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().FillListBase_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().FillListBase_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillListBase_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


