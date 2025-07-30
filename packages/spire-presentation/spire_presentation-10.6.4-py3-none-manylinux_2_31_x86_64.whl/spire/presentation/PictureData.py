from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PictureData (SpireObject) :
    """
    <summary>
        Represents a picture in a presentation.
    </summary>
    """
    @property

    def SourceEmbedImage(self)->'IImageData':
        """
    <summary>
        Gets or sets the embedded image.
            Read/write <see cref="T:Spire.Presentation.Drawing.ImageData" />.
    </summary>
        """
        GetDllLibPpt().PictureData_get_SourceEmbedImage.argtypes=[c_void_p]
        GetDllLibPpt().PictureData_get_SourceEmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureData_get_SourceEmbedImage,self.Ptr)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    @property

    def Url(self)->str:
        """
    <summary>
        Gets of sets linked image's URL.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().PictureData_get_Url.argtypes=[c_void_p]
        GetDllLibPpt().PictureData_get_Url.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().PictureData_get_Url,self.Ptr))
        return ret


    @property

    def ImageTransform(self)->'EffectDataCollection':
        """
    <summary>
        Gets the collection of image transform effects.
            Read-only <see cref="P:Spire.Presentation.Drawing.PictureData.ImageTransform" />.
    </summary>
        """
        GetDllLibPpt().PictureData_get_ImageTransform.argtypes=[c_void_p]
        GetDllLibPpt().PictureData_get_ImageTransform.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureData_get_ImageTransform,self.Ptr)
        ret = None if intPtr==None else EffectDataCollection(intPtr)
        return ret


