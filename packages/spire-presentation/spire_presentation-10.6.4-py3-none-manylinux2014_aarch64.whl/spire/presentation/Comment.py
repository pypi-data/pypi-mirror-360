from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Comment (  PptObject) :
    """
    <summary>
        Represents a comment on a slide.
    </summary>
    """
    @property

    def Text(self)->str:
        """
    <summary>
        Returns a String that represents the text in a comment
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().Comment_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Comment_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Comment_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Comment_set_Text,self.Ptr,valuePtr)

    @property

    def DateTime(self)->'DateTime':
        """
    <summary>
        Returns the date and time a comment was created.
            Read/write <see cref="T:System.DateTime" />.
    </summary>
        """
        GetDllLibPpt().Comment_get_DateTime.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_DateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Comment_get_DateTime,self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @DateTime.setter
    def DateTime(self, value:'DateTime'):
        GetDllLibPpt().Comment_set_DateTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Comment_set_DateTime,self.Ptr, value.Ptr)

    @property

    def Slide(self)->'ISlide':
        """
    <summary>
        Gets or sets the parent slide of a comment.
            Read-only <see cref="P:Spire.Presentation.Comment.Slide" />.
    </summary>
        """
        GetDllLibPpt().Comment_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Comment_get_Slide,self.Ptr)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @property

    def AuthorName(self)->str:
        """
    <summary>
        Gets or sets a String that represents the author as for a specified Comment object.
    </summary>
        """
        GetDllLibPpt().Comment_get_AuthorName.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_AuthorName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Comment_get_AuthorName,self.Ptr))
        return ret


    @AuthorName.setter
    def AuthorName(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Comment_set_AuthorName.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Comment_set_AuthorName,self.Ptr,valuePtr)

    @property

    def AuthorInitials(self)->str:
        """
    <summary>
        Gets or sets the author's initials as a read-only String for a specified Comment object
    </summary>
        """
        GetDllLibPpt().Comment_get_AuthorInitials.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_AuthorInitials.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Comment_get_AuthorInitials,self.Ptr))
        return ret


    @AuthorInitials.setter
    def AuthorInitials(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Comment_set_AuthorInitials.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Comment_set_AuthorInitials,self.Ptr,valuePtr)

    @property
    def Left(self)->float:
        """
    <summary>
        Represents the distance in points from the left edge of the comment to the left edge of the slide.
    </summary>
        """
        GetDllLibPpt().Comment_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Comment_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().Comment_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Comment_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
         Represents the distance in points from the left edge of the comment to the left edge of the slide.
    </summary>
        """
        GetDllLibPpt().Comment_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Comment_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().Comment_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Comment_set_Top,self.Ptr, value)


    def Reply(self ,author:'ICommentAuthor',reply:str,time:'DateTime'):
        """
    <summary>
        reply the comment. Do nothing if the comment is a reply
    </summary>
    <param name="author">reply author.</param>
    <param name="reply">reply.</param>
    <param name="time">time.</param>
        """
        intPtrauthor:c_void_p = author.Ptr
        intPtrtime:c_void_p = time.Ptr

        replyPtr = StrToPtr(reply)
        GetDllLibPpt().Comment_Reply.argtypes=[c_void_p ,c_void_p,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().Comment_Reply,self.Ptr, intPtrauthor,replyPtr,intPtrtime)

    @property
    def IsReply(self)->bool:
        """
    <summary>
        if the comment is reply.
    </summary>
        """
        GetDllLibPpt().Comment_get_IsReply.argtypes=[c_void_p]
        GetDllLibPpt().Comment_get_IsReply.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Comment_get_IsReply,self.Ptr)
        return ret

