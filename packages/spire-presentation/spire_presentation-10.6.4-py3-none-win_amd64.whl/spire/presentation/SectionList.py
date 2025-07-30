from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SectionList (SpireObject) :
    """

    """
    @property
    def Count(self)->int:
        """
    <summary>
        Get the count of sections in this section list.
    </summary>
        """
        GetDllLibPpt().SectionList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SectionList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SectionList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'Section':
        """
    <summary>
        Get the section by index.
    </summary>
    <param name="index">the target index.</param>
    <returns>the target section</returns>
        """
        
        GetDllLibPpt().SectionList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SectionList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def Add(self ,sectionName:str,slide:'ISlide')->'Section':
        """
    <summary>
        Add section by name and slide.
            Note: Only effect on .pptx/.potx file format,invalid other file format
    </summary>
    <param name="sectionName">the name of section.</param>
    <param name="slide">the slide contained in the section.</param>
    <returns></returns>
        """
        intPtrslide:c_void_p = slide.Ptr

        sectionNamePtr = StrToPtr(sectionName)
        GetDllLibPpt().SectionList_Add.argtypes=[c_void_p ,c_char_p,c_void_p]
        GetDllLibPpt().SectionList_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_Add,self.Ptr,sectionNamePtr,intPtrslide)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def Insert(self ,sectionIndex:int,sectionName:str)->'Section':
        """
    <summary>
        Insert section with section name and section index.
    </summary>
    <param name="sectionIndex">section index.</param>
    <param name="sectionName">section name.</param>
    <returns></returns>
        """
        
        sectionNamePtr = StrToPtr(sectionName)
        GetDllLibPpt().SectionList_Insert.argtypes=[c_void_p ,c_int,c_char_p]
        GetDllLibPpt().SectionList_Insert.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_Insert,self.Ptr, sectionIndex,sectionNamePtr)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def Append(self ,sectionName:str)->'Section':
        """
    <summary>
        Append section with section name at the end.
    </summary>
    <param name="sectionName">section name.</param>
    <returns></returns>
        """
        
        sectionNamePtr = StrToPtr(sectionName)
        GetDllLibPpt().SectionList_Append.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().SectionList_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_Append,self.Ptr,sectionNamePtr)
        ret = None if intPtr==None else Section(intPtr)
        return ret



    def IndexOf(self ,section:'Section')->int:
        """
    <summary>
        Get the index of the section.
    </summary>
    <param name="section">The target section.</param>
    <returns></returns>
        """
        intPtrsection:c_void_p = section.Ptr

        GetDllLibPpt().SectionList_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SectionList_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SectionList_IndexOf,self.Ptr, intPtrsection)
        return ret


    def MoveSlide(self ,section:'Section',index:int,slide:'ISlide'):
        """
    <summary>
        Move the position of slide in the section.
    </summary>
    <param name="section">The target section.</param>
    <param name="index">The target position.</param>
    <param name="slide">The target slide.</param>
        """
        intPtrsection:c_void_p = section.Ptr
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SectionList_MoveSlide.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().SectionList_MoveSlide,self.Ptr, intPtrsection,index,intPtrslide)


    def InsertSlide(self ,section:'Section',index:int,slide:'ISlide')->'ISlide':
        """
    <summary>
        Insert slide into the section at position.
    </summary>
    <param name="section">The target section.</param>
    <param name="index">The target position.</param>
    <param name="slide">The target slide.</param>
    <returns></returns>
        """
        intPtrsection:c_void_p = section.Ptr
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SectionList_InsertSlide.argtypes=[c_void_p ,c_void_p,c_int,c_void_p]
        GetDllLibPpt().SectionList_InsertSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SectionList_InsertSlide,self.Ptr, intPtrsection,index,intPtrslide)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret



    def RemoveSlide(self ,section:'Section',index:int):
        """
    <summary>
        Remove the slide at some position in the section.
    </summary>
    <param name="section">The target section.</param>
    <param name="index">The position of target slide.</param>
        """
        intPtrsection:c_void_p = section.Ptr

        GetDllLibPpt().SectionList_RemoveSlide.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt().SectionList_RemoveSlide,self.Ptr, intPtrsection,index)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Remove section at some position.
    </summary>
    <param name="index">position in section list.</param>
        """
        
        GetDllLibPpt().SectionList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().SectionList_RemoveAt,self.Ptr, index)

    def RemoveAll(self):
        """
    <summary>
        Remove all section.
    </summary>
        """
        GetDllLibPpt().SectionList_RemoveAll.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().SectionList_RemoveAll,self.Ptr)

