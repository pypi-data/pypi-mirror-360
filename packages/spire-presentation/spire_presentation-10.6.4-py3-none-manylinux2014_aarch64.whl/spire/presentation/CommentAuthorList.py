from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommentAuthorList (SpireObject) :
    """

    """
    @property
    def Count(self)->int:
        """

        """
        GetDllLibPpt().CommentAuthorList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
         
        GetDllLibPpt().CommentAuthorList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentAuthorList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ICommentAuthor(intPtr)
        return ret

    def get_Item(self ,index:int)->'ICommentAuthor':
        """

        """
        
        GetDllLibPpt().CommentAuthorList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentAuthorList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ICommentAuthor(intPtr)
        return ret



    def AddAuthor(self ,name:str,initials:str)->'ICommentAuthor':
        """
    <summary>
        Add new author at the end of a collection.
    </summary>
    <param name="name">Name of a new author.</param>
    <param name="initials">Initials of a new author.</param>
    <returns>ICommentAuthor</returns>
        """
        
        namePtr = StrToPtr(name)
        initialsPtr = StrToPtr(initials)
        GetDllLibPpt().CommentAuthorList_AddAuthor.argtypes=[c_void_p ,c_char_p,c_char_p]
        GetDllLibPpt().CommentAuthorList_AddAuthor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_AddAuthor,self.Ptr,namePtr,initialsPtr)
        ret = None if intPtr==None else ICommentAuthor(intPtr)
        return ret


#
#    def ToArray(self)->List['ICommentAuthor']:
#        """
#
#        """
#        GetDllLibPpt().CommentAuthorList_ToArray.argtypes=[c_void_p]
#        GetDllLibPpt().CommentAuthorList_ToArray.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().CommentAuthorList_ToArray,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, ICommentAuthor)
#        return ret



    def FindByName(self ,name:str)->List['ICommentAuthor']:
       """
   <summary>
       Find author in a collection by name.
   </summary>
   <param name="name">Name of an author to find.</param>
   <returns>Authors or null.</returns>
       """
       namePtr = StrToPtr(name)
       GetDllLibPpt().CommentAuthorList_FindByName.argtypes=[c_void_p ,c_char_p]
       GetDllLibPpt().CommentAuthorList_FindByName.restype=IntPtrArray
       intPtrArray = CallCFunction(GetDllLibPpt().CommentAuthorList_FindByName,self.Ptr, namePtr)
       ret = GetObjVectorFromArray(intPtrArray, ICommentAuthor)
       return ret


#
#    def FindByNameAndInitials(self ,name:str,initials:str)->List['ICommentAuthor']:
#        """
#    <summary>
#        Find author in a collection by name and initials
#    </summary>
#    <param name="name">Name of an author to find.</param>
#    <param name="initials">Initials of an author to find.</param>
#    <returns>Authors or null.</returns>
#        """
#        
#        GetDllLibPpt().CommentAuthorList_FindByNameAndInitials.argtypes=[c_void_p ,c_wchar_p,c_wchar_p]
#        GetDllLibPpt().CommentAuthorList_FindByNameAndInitials.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().CommentAuthorList_FindByNameAndInitials,self.Ptr, name,initials)
#        ret = GetObjVectorFromArray(intPtrArray, ICommentAuthor)
#        return ret



    def GetEnumerator(self)->'IEnumerator':
        """

        """
        GetDllLibPpt().CommentAuthorList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().CommentAuthorList_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().CommentAuthorList_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentAuthorList_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


