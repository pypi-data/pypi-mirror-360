from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SequenceCollection (  IEnumerable) :
    """
    <summary>
        Represent collection of interactive sequences.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements in a collection
    </summary>
        """
        GetDllLibPpt().SequenceCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SequenceCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SequenceCollection_get_Count,self.Ptr)
        return ret


    def Add(self ,shape:'IShape')->'AnimationEffectCollection':
        """
    <summary>
        Add new interactive sequence.
            Read/write <see cref="T:Spire.Presentation.Collections.AnimationEffectCollection" />.
    </summary>
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().SequenceCollection_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SequenceCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SequenceCollection_Add,self.Ptr, intPtrshape)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret



    def Remove(self ,item:'AnimationEffectCollection'):
        """
    <summary>
        Removes specified sequence from a collection.
    </summary>
    <param name="item">Sequence to remove.</param>
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().SequenceCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().SequenceCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes sequence at the specified index.
    </summary>
    <param name="index"></param>
        """
        
        GetDllLibPpt().SequenceCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().SequenceCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
    <summary>
        Removes all sequences from a collection.
    </summary>
        """
        GetDllLibPpt().SequenceCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().SequenceCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'AnimationEffectCollection':
        """
    <summary>
        Gets a sequense at the specified index.
    </summary>
    <param name="index"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().SequenceCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SequenceCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SequenceCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an iterator for a collection.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().SequenceCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().SequenceCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SequenceCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


