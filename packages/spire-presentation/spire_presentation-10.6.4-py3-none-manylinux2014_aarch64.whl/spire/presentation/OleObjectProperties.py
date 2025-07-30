from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OleObjectProperties (  ICollection, IEnumerable) :
    """
    <summary>
        A collection of OleObject properties.
    </summary>
    """

    def Add(self ,name:str,value:str):
        """
    <summary>
        Adds a property to the collection.
    </summary>
    <param name="name">The name of the property.</param>
    <param name="value">The alue of the property.</param>
        """
        
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().OleObjectProperties_Add.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_Add,self.Ptr,namePtr,valuePtr)


    def Remove(self ,name:str):
        """
    <summary>
        Removes a property with the specified name.
    </summary>
    <param name="name">The name of property to remove.</param>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().OleObjectProperties_Remove.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_Remove,self.Ptr,namePtr)



    def get_Item(self ,name:str)->str:
        """
    <summary>
        Gets or sets property.
    </summary>
    <param name="name">Name of property.</param>
    <returns></returns>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().OleObjectProperties_get_Item.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().OleObjectProperties_get_Item.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().OleObjectProperties_get_Item,self.Ptr, namePtr))
        return ret

    def Keys(self)->List[str]:
        """
    <summary>
        Gets or sets property.
    </summary>
    <param name="name">Name of property.</param>
    <returns></returns>
        """
        
        GetDllLibPpt().OleObjectProperties_get_Keys.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_Keys.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().OleObjectProperties_get_Keys,self.Ptr)
        ret = GetStringPtrArray(intPtrArray)
        return ret



    def set_Item(self ,name:str,value:str):
        """

        """
        
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().OleObjectProperties_set_Item.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_set_Item,self.Ptr,namePtr,valuePtr)

    def Clear(self):
        """
    <summary>
        Removes all properties.
    </summary>
        """
        GetDllLibPpt().OleObjectProperties_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_Clear,self.Ptr)

#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all property-value pairs to the specified array.
#    </summary>
#    <param name="array">The target array.</param>
#    <param name="index">Index in the target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().OleObjectProperties_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().OleObjectProperties_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def Count(self)->int:
        """
    <summary>
        Gets a number of properties in the collection.
    </summary>
        """
        GetDllLibPpt().OleObjectProperties_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().OleObjectProperties_get_Count,self.Ptr)
        return ret

    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().OleObjectProperties_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OleObjectProperties_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().OleObjectProperties_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectProperties_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for entire collection.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().OleObjectProperties_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectProperties_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


