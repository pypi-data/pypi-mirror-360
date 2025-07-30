from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Section (SpireObject) :
    """

    """
#    @property
#
#    def SlideIdList(self)->'List1':
#        """
#    <summary>
#        get IDs of slides in this section.
#    </summary>
#        """
#        GetDllLibPpt().Section_get_SlideIdList.argtypes=[c_void_p]
#        GetDllLibPpt().Section_get_SlideIdList.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().Section_get_SlideIdList,self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    def GetSlides(self)->List['ISlide']:
        """
    <summary>
        get slides in this section.
    </summary>
    <returns>Array of ISlide</returns>
        """
        GetDllLibPpt().Section_GetSlides.argtypes=[c_void_p]
        GetDllLibPpt().Section_GetSlides.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Section_GetSlides,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, ISlide)
        return ret



    def Move(self ,index:int,slide:'ISlide'):
        """
    <summary>
        Move the position of slide in section.
    </summary>
    <param name="index">the target position.</param>
    <param name="slide">the slide which needs moved.</param>
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().Section_Move.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().Section_Move,self.Ptr, index,intPtrslide)


    def Insert(self ,index:int,slide:'ISlide')->'ISlide':
        """
    <summary>
        Insert slide into section.
    </summary>
    <param name="index">the target position.</param>
    <param name="slide">the target slide.</param>
    <returns></returns>
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().Section_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().Section_Insert.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Section_Insert,self.Ptr, index,intPtrslide)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret



    def AddRange(self ,slides:'IList'):
        slide_ptrs = [s.Ptr for s in slides]

        num_slides = len(slide_ptrs)
        slide_ptr_array = (c_void_p * num_slides)(*slide_ptrs)
        GetDllLibPpt().Section_AddRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().Section_AddRange,self.Ptr, slide_ptr_array,num_slides)



    def RemoveAt(self ,index:int):
        """
    <summary>
        remove slide at some position
    </summary>
    <param name="index">the target position.</param>
        """
        
        GetDllLibPpt().Section_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().Section_RemoveAt,self.Ptr, index)


    def Remove(self ,slide:'ISlide'):
        """
    <summary>
        Remove a slide.
    </summary>
    <param name="slide">target slide.</param>
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().Section_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().Section_Remove,self.Ptr, intPtrslide)


    def RemoveRange(self ,startIndex:int,count:int):
        """
    <summary>
        Remove a range of slides.
    </summary>
    <param name="startIndex">start index.</param>
    <param name="count">the count of slides.</param>
        """
        
        GetDllLibPpt().Section_RemoveRange.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().Section_RemoveRange,self.Ptr, startIndex,count)

    @property

    def Name(self)->str:
        """
    <summary>
        Get or set the name of this section.
    </summary>
        """
        GetDllLibPpt().Section_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().Section_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Section_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Section_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Section_set_Name,self.Ptr,valuePtr)

    @property

    def Id(self)->str:
        """

        """
        GetDllLibPpt().Section_get_Id.argtypes=[c_void_p]
        GetDllLibPpt().Section_get_Id.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Section_get_Id,self.Ptr))
        return ret


    @Id.setter
    def Id(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Section_set_Id.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Section_set_Id,self.Ptr,valuePtr)

    @property
    def Index(self)->int:
        """
    <summary>
        Get the position of this section in section list.
    </summary>
        """
        GetDllLibPpt().Section_get_Index.argtypes=[c_void_p]
        GetDllLibPpt().Section_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Section_get_Index,self.Ptr)
        return ret

