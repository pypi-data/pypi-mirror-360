from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommentList (SpireObject) :
    """
    <summary>
        Represents a collection of comments of one author.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().CommentList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CommentList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommentList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().CommentList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Comment(intPtr)
        return ret

    def get_Item(self ,index:int)->'Comment':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.Comment" />.
    </summary>
        """
        
        GetDllLibPpt().CommentList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommentList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Comment(intPtr)
        return ret



    def AppendComment(self ,slide:'ISlide',text:str,x:float,y:float)->'Comment':
        """
    <summary>
        Adds a new comment added to a slide.
    </summary>
    <param name="slide">Slide object</param>
    <param name="text">Text of new comment.</param>
    <param name="x">x position</param>
    <param name="y">y position</param>
    <returns></returns>
        """
        intPtrslide:c_void_p = slide.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().CommentList_AppendComment.argtypes=[c_void_p ,c_void_p,c_char_p,c_float,c_float]
        GetDllLibPpt().CommentList_AppendComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_AppendComment,self.Ptr, intPtrslide,textPtr,x,y)
        ret = None if intPtr==None else Comment(intPtr)
        return ret



    def InsertComment(self ,slide:'ISlide',Index:int,text:str,x:float,y:float)->'Comment':
        """
    <summary>
        Adds a new comment added to a slide.
    </summary>
    <param name="slide">Slide object</param>
    <param name="Index">Text of new comment.</param>
    <param name="text"></param>
    <param name="x">x position</param>
    <param name="y">y position</param>
    <returns></returns>
        """
        intPtrslide:c_void_p = slide.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().CommentList_InsertComment.argtypes=[c_void_p ,c_void_p,c_int,c_char_p,c_float,c_float]
        GetDllLibPpt().CommentList_InsertComment.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_InsertComment,self.Ptr, intPtrslide,Index,textPtr,x,y)
        ret = None if intPtr==None else Comment(intPtr)
        return ret


#    @dispatch
#
#    def ToArray(self)->List[Comment]:
#        """
#
#        """
#        GetDllLibPpt().CommentList_ToArray.argtypes=[c_void_p]
#        GetDllLibPpt().CommentList_ToArray.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().CommentList_ToArray,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Comment)
#        return ret


#    @dispatch
#
#    def ToArray(self ,startIndex:int,count:int)->List[Comment]:
#        """
#
#        """
#        
#        GetDllLibPpt().CommentList_ToArraySC.argtypes=[c_void_p ,c_int,c_int]
#        GetDllLibPpt().CommentList_ToArraySC.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().CommentList_ToArraySC,self.Ptr, startIndex,count)
#        ret = GetObjVectorFromArray(intPtrArray, Comment)
#        return ret



    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the element at the specified index in a collection.
    </summary>
    <param name="index">The zero-based index of the element to remove.</param>
        """
        
        GetDllLibPpt().CommentList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().CommentList_RemoveAt,self.Ptr, index)


    def Remove(self ,comment:'Comment'):
        """
    <summary>
        Removes the first occurrence of the specified comment in a collection.
    </summary>
    <param name="comment">The comment to remove from a collection.</param>
        """
        intPtrcomment:c_void_p = comment.Ptr

        GetDllLibPpt().CommentList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().CommentList_Remove,self.Ptr, intPtrcomment)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().CommentList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CommentList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
    <summary>
        Gets parent PresentationPptx object for a collection of comments.
            Read-only <see cref="T:Spire.Presentation.PresentationPptx" />.
    </summary>
        """
        GetDllLibPpt().CommentList_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().CommentList_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommentList_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


