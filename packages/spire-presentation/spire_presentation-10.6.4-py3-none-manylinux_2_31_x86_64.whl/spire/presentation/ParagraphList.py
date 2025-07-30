from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ParagraphList (  IActiveSlide) :
    """
    <summary>
        Represents a collection of a paragraphs.
    </summary>
    """

    def AddFromHtml(self ,htmlText:str):
        """
    <summary>
        Adds text from specified html string.
    </summary>
    <param name="htmlText">HTML text.</param>
        """
        
        htmlTextPtr = StrToPtr(htmlText)
        GetDllLibPpt().ParagraphList_AddFromHtml.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().ParagraphList_AddFromHtml,self.Ptr,htmlTextPtr)

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
    </summary>
        """
        GetDllLibPpt().ParagraphList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().ParagraphList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ParagraphList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret

    def get_Item(self ,index:int)->'TextParagraph':
        """
    <summary>
        Gets the element at the specified index.
    </summary>
        """
        
        GetDllLibPpt().ParagraphList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ParagraphList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret

    
    def Append(self ,value:'TextParagraph')->int:
        """
    <summary>
        Adds a Paragraph to the end of collection.
    </summary>
    <param name="value">The Paragraph </param>
    <returns>The index at which the Paragraph has been added.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphList_Append,self.Ptr, intPtrvalue)
        return ret

    
    def AppendCollection(self ,value:'ParagraphCollection')->int:
        """
    <summary>
        Adds a content of Paragraphs to the end of collection.
    </summary>
    <param name="value">The ParagraphCollection </param>
    <returns>The index at which the Paragraph has been added or -1 if there are nothing to add.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_AppendV.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphList_AppendV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphList_AppendV,self.Ptr, intPtrvalue)
        return ret

    @dispatch

    def Insert(self ,index:int,value:'TextParagraph'):
        """
    <summary>
        Inserts a Paragraph into the collection at the specified index.
    </summary>
    <param name="index">The zero-based index at which Paragraph should be inserted.</param>
    <param name="value">The Paragraph to insert.</param>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphList_Insert,self.Ptr, index,intPtrvalue)

    @dispatch

    def InsertCollection(self ,index:int,value:'ParagraphCollection'):
        """
    <summary>
        Inserts a content of ParagraphExCollection into the collection at the specified index.
    </summary>
    <param name="index">The zero-based index at which paragraphs should be inserted.</param>
    <param name="value">The paragraphs to insert.</param>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ParagraphList_InsertIV.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphList_InsertIV,self.Ptr, index,intPtrvalue)

    def Clear(self):
        """
    <summary>
        Removes all elements from the collection.
    </summary>
        """
        GetDllLibPpt().ParagraphList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphList_Clear,self.Ptr)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the element at the specified index of the collection.
    </summary>
    <param name="index">The zero-based index of the element to remove.</param>
        """
        
        GetDllLibPpt().ParagraphList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ParagraphList_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().ParagraphList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ParagraphList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphList_Equals,self.Ptr, intPtrobj)
        return ret

