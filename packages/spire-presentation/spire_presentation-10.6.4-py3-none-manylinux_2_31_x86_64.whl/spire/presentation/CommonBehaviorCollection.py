from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommonBehaviorCollection (  SpireObject) :
    """
    <summary>
        Represents collection of behavior effects.
    </summary>
    """
    @dispatch
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().CommonBehaviorCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommonBehaviorCollection_get_Item.restype=IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_get_Item,self.Ptr, key)
        ret = None if intPtrWithTypeName==None else self._create(intPtrWithTypeName)
        return ret

    @staticmethod
    def _create(intPtrWithTypeName:IntPtrWithTypeName)->'CommonBehavior':
        from spire.presentation import AnimationColorBehavior
        from spire.presentation import AnimationCommandBehavior
        from spire.presentation import AnimationFilterEffect
        from spire.presentation import AnimationMotion
        from spire.presentation import AnimationProperty
        from spire.presentation import AnimationRotation
        from spire.presentation import AnimationScale
        from spire.presentation import AnimationSet
        from spire.presentation import CommonBehavior

        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'Spire.Presentation.Drawing.Animation.AnimationColorBehavior'):
            ret = AnimationColorBehavior(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationCommandBehavior'):
            ret = AnimationCommandBehavior(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationFilterEffect'):
            ret = AnimationFilterEffect(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationMotion'):
            ret = AnimationMotion(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationProperty'):
            ret = AnimationProperty(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationRotation'):
            ret = AnimationRotation(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationScale'):
            ret = AnimationScale(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationSet'):
            ret = AnimationSet(intPtr)
        else:
            ret = CommonBehavior(intPtr)

        return ret

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of behaviors in a collection.
    </summary>
        """
        GetDllLibPpt().CommonBehaviorCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_get_Count,self.Ptr)
        return ret


    def Append(self ,item:'CommonBehavior')->int:
        """
    <summary>
        Add new behavior to a collection.
    </summary>
    <param name="item">Behavior to add.</param>
    <returns>Index of a new behavior in a collection.</returns>
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Append,self.Ptr, intPtritem)
        return ret


    def Insert(self ,index:int,item:'CommonBehavior'):
        """
    <summary>
        Inserts new behavior to a collection at the specified index.
    </summary>
    <param name="index">Index where new behavior should be inserted.</param>
    <param name="item">Behavior to insert.</param>
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Insert,self.Ptr, index,intPtritem)


    def Remove(self ,item:'CommonBehavior'):
        """
    <summary>
        Removes specified behavior from a collection.
    </summary>
    <param name="item">Behavior to remove.</param>
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes behavior from a collection at the specified index.
    </summary>
    <param name="index">Index of a behavior to remove.</param>
        """
        
        GetDllLibPpt().CommonBehaviorCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
    <summary>
        Removes all behaviors from a collection.
    </summary>
        """
        GetDllLibPpt().CommonBehaviorCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'CommonBehavior':
        """
    <summary>
        Retirns a behavior at the specified index.
    </summary>
    <param name="index">Index of a behavior to return.</param>
    <returns>Animation begavior.</returns>
        """
        
        GetDllLibPpt().CommonBehaviorCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommonBehaviorCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else CommonBehavior(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an iterator for the entire collection.
    </summary>
    <returns>Iterator.</returns>
        """
        GetDllLibPpt().CommonBehaviorCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


