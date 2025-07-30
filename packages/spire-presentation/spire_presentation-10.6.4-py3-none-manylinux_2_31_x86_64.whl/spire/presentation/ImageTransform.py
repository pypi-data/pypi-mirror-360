from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ImageTransform (  IEnumerable, IActiveSlide, IActivePresentation) :
    """
    <summary>
        Represents a collection of effects apllied to an image.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of image effects in a collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ImageTransform_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ImageTransform_get_Count,self.Ptr)
        return ret


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes an image effect from a collection at the specified index.
    </summary>
    <param name="index">Index of an image effect that should be deleted.</param>
        """
        
        GetDllLibPpt().ImageTransform_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ImageTransform_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
    <summary>
        Removes all image effects from a collection.
    </summary>
        """
        GetDllLibPpt().ImageTransform_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ImageTransform_Clear,self.Ptr)


    def Add(self ,base:'ImageTransformBase')->int:
        """
    <summary>
        Adds the new image effect to the end of a collection.
    </summary>
    <param name="base">The image effect to add to the end of a collection.</param>
    <returns>Index of the new image effect in a collection.</returns>
        """
        intPtrbase:c_void_p = base.Ptr

        GetDllLibPpt().ImageTransform_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ImageTransform_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ImageTransform_Add,self.Ptr, intPtrbase)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().ImageTransform_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def get_Item(self ,index:int)->'ImageTransformBase':
        """
    <summary>
        Gets an <see cref="T:Spire.Presentation.Drawing.ImageTransformBase" /> from the collection by it's index.
    </summary>
    <param name="index"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().ImageTransform_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ImageTransform_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ImageTransformBase(intPtr)
        return ret


    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide for an ImageTransform collection.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().ImageTransform_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
    <summary>
        Gets the parent presentation for an ImageTransform collection.
            Read-only <see cref="T:Spire.Presentation.PresentationPptx" />.
    </summary>
        """
        GetDllLibPpt().ImageTransform_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ImageTransform_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ImageTransform_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


