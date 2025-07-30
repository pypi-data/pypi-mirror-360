from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectStyleList (  IEnumerable) :
    """
    <summary>
        Represents a collection of effect styles.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets a number of elements in the collection.
            Readonly <see cref="T:System.Int32" />,
    </summary>
        """
        GetDllLibPpt().EffectStyleList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().EffectStyleList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'EffectStyle':
        """
    <summary>
        Gets an element at specified position.
            Readonly <see cref="T:Spire.Presentation.Drawing.EffectStyle" />.
    </summary>
    <param name="index">Position of element.</param>
    <returns>Element at specified position.</returns>
        """
        
        GetDllLibPpt().EffectStyleList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EffectStyleList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyleList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else EffectStyle(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectStyleList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectStyleList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyleList_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
        """
        GetDllLibPpt().EffectStyleList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyleList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyleList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


