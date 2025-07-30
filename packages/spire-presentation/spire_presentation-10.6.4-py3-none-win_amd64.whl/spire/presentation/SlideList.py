from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideList (SpireObject) :

    """
    <summary>
        Represents a collection of a slides.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
    </summary>
        """
        GetDllLibPpt().SlideList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SlideList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_get_Count,self.Ptr)
        return ret

     #support x[]
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().SlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_get_Item,self.Ptr, key)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret

    def get_Item(self ,index:int)->'ISlide':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.Slide" />.
    </summary>
        """
        
        GetDllLibPpt().SlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def Append(self)->ISlide:
        """
    <summary>
        Append new slide.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().SlideList_Append.argtypes=[c_void_p]
        GetDllLibPpt().SlideList_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_Append,self.Ptr)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def AppendByLayoutType(self ,templateType:SlideLayoutType):
        """

        """
        enumtemplateType:c_int = templateType.value

        GetDllLibPpt().SlideList_AppendT.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_AppendT.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_AppendT,self.Ptr, enumtemplateType)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def AppendBySlide(self ,slide:ISlide)->int:
        """
    <summary>
        Adds a slide to the collection.
    </summary>
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideList_AppendS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideList_AppendS.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_AppendS,self.Ptr, intPtrslide)
        return ret

    @dispatch

    def Insert(self ,index:int,slide:ISlide):
        """
    <summary>
        Inserts a slide to the collection.
    </summary>
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_Insert,self.Ptr, index,intPtrslide)

    @dispatch

    def Insert(self ,index:int)->ISlide:
        """
    <summary>
        Insert a empty slide to collection.
    </summary>
    <param name="index"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().SlideList_InsertI.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_InsertI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_InsertI,self.Ptr, index)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def InsertByLayoutType(self ,index:int,templateType:SlideLayoutType)->ISlide:
        """
    <summary>
        Insert a slide to collection.
    </summary>
    <param name="index"></param>
    <param name="templateType"></param>
    <returns></returns>
        """
        enumtemplateType:c_int = templateType.value

        GetDllLibPpt().SlideList_InsertIT.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().SlideList_InsertIT.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_InsertIT,self.Ptr, index,enumtemplateType)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def Append(self ,slide:ISlide,layout:ILayout)->int:
        """

        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrlayout:c_void_p = layout.Ptr

        GetDllLibPpt().SlideList_AppendSL.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().SlideList_AppendSL.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_AppendSL,self.Ptr, intPtrslide,intPtrlayout)
        return ret

    @dispatch

    def Insert(self ,index:int,slide:ISlide,layout:ILayout):
        """

        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrlayout:c_void_p = layout.Ptr

        GetDllLibPpt().SlideList_InsertISL.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_InsertISL,self.Ptr, index,intPtrslide,intPtrlayout)

    @dispatch

    def AppendByMaster(self ,slide:ISlide,master:IMasterSlide)->int:
        """
    <summary>
        Adds a slide to the collection.
    </summary>
        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrmaster:c_void_p = master.Ptr

        GetDllLibPpt().SlideList_AppendSM.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().SlideList_AppendSM.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_AppendSM,self.Ptr, intPtrslide,intPtrmaster)
        return ret

    @dispatch

    def InsertByMaster(self ,index:int,slide:ISlide,master:IMasterSlide):
        """
    <summary>
        Inserts a slide to the collection.
    </summary>
        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrmaster:c_void_p = master.Ptr

        GetDllLibPpt().SlideList_InsertISM.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_InsertISM,self.Ptr, index,intPtrslide,intPtrmaster)


    def Remove(self ,value:'ISlide'):
        """
    <summary>
        Removes the first occurrence of a specific object from the collection.
    </summary>
    <param name="value">The slide to remove from the collection.</param>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().SlideList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_Remove,self.Ptr, intPtrvalue)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the element at the specified index of the collection.
    </summary>
    <param name="index">The zero-based index of the element to remove.</param>
        """
        
        GetDllLibPpt().SlideList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().SlideList_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().SlideList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().SlideList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


#    @dispatch
#
#    def ToArray(self)->List[ISlide]:
#        """
#    <summary>
#        Creates and returns an array with all slides in it.
#    </summary>
#    <returns>Array of <see cref="T:Spire.Presentation.Slide" /></returns>
#        """
#        GetDllLibPpt().SlideList_ToArray.argtypes=[c_void_p]
#        GetDllLibPpt().SlideList_ToArray.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().SlideList_ToArray,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, ISlide)
#        return ret


#    @dispatch
#
#    def ToArray(self ,startIndex:int,count:int)->List[ISlide]:
#        """
#
#        """
#        
#        GetDllLibPpt().SlideList_ToArraySC.argtypes=[c_void_p ,c_int,c_int]
#        GetDllLibPpt().SlideList_ToArraySC.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().SlideList_ToArraySC,self.Ptr, startIndex,count)
#        ret = GetObjVectorFromArray(intPtrArray, ISlide)
#        return ret



    def Move(self ,newIndex:int,OldIndex:int):
        """
    <summary>
        Moves slide from the collection to the specified position.
    </summary>
    <param name="newIndex">Target index.</param>
    <param name="OldIndex">move from.</param>
        """
        
        GetDllLibPpt().SlideList_Move.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().SlideList_Move,self.Ptr, newIndex,OldIndex)


    def IndexOf(self ,slide:'ISlide')->int:
        """

        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideList_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideList_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_IndexOf,self.Ptr, intPtrslide)
        return ret

