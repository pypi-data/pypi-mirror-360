from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TagList (SpireObject) :
    """
    <summary>
        Represents the collection of tags
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets a number of tags in the collectoin.
    </summary>
        """
        GetDllLibPpt().TagList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TagList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TagList_get_Count,self.Ptr)
        return ret


    def Append(self ,name:str,value:str)->int:
        """
    <summary>
        Adds a new tag to collection.
    </summary>
    <param name="name">The name of the tag.</param>
    <param name="value">The value of the tag.</param>
    <returns>The index of the added tag.</returns>
        """
        
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TagList_Append.argtypes=[c_void_p ,c_char_p,c_char_p]
        GetDllLibPpt().TagList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TagList_Append,self.Ptr,namePtr,valuePtr)
        return ret


    def Remove(self ,name:str):
        """
    <summary>
        Removes the tag with a specified name from the collection.
    </summary>
    <param name="name">The name of tag to remove.</param>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_Remove.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().TagList_Remove,self.Ptr,namePtr)


    def IndexOfKey(self ,name:str)->int:
        """
    <summary>
        Gets the zero-based index of the specified key in the collection.
    </summary>
    <param name="name">The name to locate in the collection.</param>
    <returns>The zero-based index of key, if key is found in the collection; otherwise, -1.</returns>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_IndexOfKey.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().TagList_IndexOfKey.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TagList_IndexOfKey,self.Ptr,namePtr)
        return ret


    def Contains(self ,name:str)->bool:
        """
    <summary>
        Indicates whether the collection contains a specific name.
    </summary>
    <param name="name">The key to locate.</param>
    <returns>True if the collection contains an tag with the specified key; otherwise, false.</returns>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_Contains.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().TagList_Contains.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TagList_Contains,self.Ptr,namePtr)
        return ret


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the tag at the specified index.
    </summary>
    <param name="index">The zero-based index of the tag to remove.</param>
        """
        
        GetDllLibPpt().TagList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TagList_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
    <summary>
        Removes all tags from the collection.
    </summary>
        """
        GetDllLibPpt().TagList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TagList_Clear,self.Ptr)


    def GetByInd(self ,index:int)->str:
        """
    <summary>
        Gets value of a tag at the specified index.
    </summary>
    <param name="index">Index of a tag to return.</param>
    <returns>Value of a tag.</returns>
        """
        
        GetDllLibPpt().TagList_GetByInd.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TagList_GetByInd.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TagList_GetByInd,self.Ptr, index))
        return ret



    def GetKey(self ,index:int)->str:
        """
    <summary>
        Gets key of a tag at the specified index.
    </summary>
    <param name="index">Index of a tag to return.</param>
    <returns>Key of a tag.</returns>
        """
        
        GetDllLibPpt().TagList_GetKey.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TagList_GetKey.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TagList_GetKey,self.Ptr, index))
        return ret



    def get_Item(self ,name:str)->str:
        """
    <summary>
        Gets or sets a key and a value pair of a tag.
    </summary>
    <param name="name">Key of a tag.</param>
    <returns>Value of a tag.</returns>
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_get_Item.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().TagList_get_Item.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TagList_get_Item,self.Ptr, name))
        return ret



    def set_Item(self ,name:str,value:str):
        """

        """
        
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TagList_set_Item.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().TagList_set_Item,self.Ptr,namePtr,valuePtr)

