from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationEffectCollection ( SpireObject) :

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().AnimationEffectCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().AnimationEffectCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret
    """
    <summary>
        Represent collection of effects.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of effects in a sequense.
    </summary>
        """
        GetDllLibPpt().AnimationEffectCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffectCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_Count,self.Ptr)
        return ret


    def Remove(self ,item:'AnimationEffect'):
        """
    <summary>
        Removes specified effect from a collection.
    </summary>
    <param name="item">Effect to remove.</param>
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().AnimationEffectCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes an effect from a collection.
    </summary>
    <param name="index"></param>
        """
        
        GetDllLibPpt().AnimationEffectCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
    <summary>
        Removes all effects from a collection.
    </summary>
        """
        GetDllLibPpt().AnimationEffectCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'AnimationEffect':
        """
    <summary>
        Gets an effect at the specified index.
    </summary>
    <param name="index"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().AnimationEffectCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().AnimationEffectCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an iterator for a collection.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().AnimationEffectCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffectCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def TriggerShape(self)->'Shape':
        """

        """
        GetDllLibPpt().AnimationEffectCollection_get_TriggerShape.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffectCollection_get_TriggerShape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_TriggerShape,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @TriggerShape.setter
    def TriggerShape(self, value:'Shape'):
        GetDllLibPpt().AnimationEffectCollection_set_TriggerShape.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_set_TriggerShape,self.Ptr, value.Ptr)


    def AddEffect(self ,shape:'IShape',animationEffectType:'AnimationEffectType')->'AnimationEffect':
        """
    <summary>
        Add new effect to the end of sequence.
    </summary>
    <param name="shape"></param>
    <param name="animationEffectType"></param>
    <returns></returns>
        """
        intPtrshape:c_void_p = shape.Ptr
        enumanimationEffectType:c_int = animationEffectType.value

        GetDllLibPpt().AnimationEffectCollection_AddEffect.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibPpt().AnimationEffectCollection_AddEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_AddEffect,self.Ptr, intPtrshape,enumanimationEffectType)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().AnimationEffectCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().AnimationEffectCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().AnimationEffectCollection_Equals,self.Ptr, intPtrobj)
        return ret

