from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EmbedImageList ( SpireObject ) :
    """
    <summary>
        Summary description for Images.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets a number of images in the collection.
    </summary>
        """
        GetDllLibPpt().EmbedImageList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().EmbedImageList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().EmbedImageList_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().EmbedImageList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EmbedImageList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret

    def get_Item(self ,index:int)->'IImageData':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.Drawing.ImageData" />.
    </summary>
        """
        
        GetDllLibPpt().EmbedImageList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().EmbedImageList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret

    def AppendImageData(self ,embedImage:IImageData)->IImageData:
        """
    <summary>
        Adds a copy of an image from an another presentation.
    </summary>
    <param name="embedImage">Source image.</param>
    <returns>Added image.</returns>
        """
        intPtrembedImage:c_void_p = embedImage.Ptr

        GetDllLibPpt().EmbedImageList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EmbedImageList_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_Append,self.Ptr, intPtrembedImage)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    #@dispatch

    #def Append(self ,image:'Stream')->IImageData:
    #    """
    #<summary>
    #    Add an image to a presentation.
    #</summary>
    #<param name="image">Image to add.</param>
    #<returns>Added image.</returns>
    #    """
    #    intPtrimage:c_void_p = image.Ptr

    #    GetDllLibPpt().EmbedImageList_AppendI.argtypes=[c_void_p ,c_void_p]
    #    GetDllLibPpt().EmbedImageList_AppendI.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_AppendI,self.Ptr, intPtrimage)
    #    ret = None if intPtr==None else IImageData(intPtr)
    #    return ret

    def AppendStream(self ,stream:'Stream')->'IImageData':
        """
    <summary>
        Add an image to a presentation from stream.
    </summary>
    <param name="stream">Stream to add image from.</param>
    <returns>Added image.</returns>
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().EmbedImageList_AppendS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EmbedImageList_AppendS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_AppendS,self.Ptr, intPtrstream)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().EmbedImageList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().EmbedImageList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EmbedImageList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


