from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
from spire.presentation.IImageData import IImageData

class PictureShape (  IActiveSlide) :
    """
    <summary>
        Represents a picture in a presentation.
    </summary>
    """
    @property

    def EmbedImage(self)->'IImageData':
        """
    <summary>
        Gets or sets the embedded image.
            Read/write <see cref="P:Spire.Presentation.PictureShape.EmbedImage" />.
    </summary>
        """
        GetDllLibPpt().PictureShape_get_EmbedImage.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_EmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureShape_get_EmbedImage,self.Ptr)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    @EmbedImage.setter
    def EmbedImage(self, value:'IImageData'):
        GetDllLibPpt().PictureShape_set_EmbedImage.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().PictureShape_set_EmbedImage,self.Ptr, value.Ptr)

    @property

    def Url(self)->str:
        """
    <summary>
        Gets or sets linked image's URL.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().PictureShape_get_Url.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Url.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().PictureShape_get_Url,self.Ptr))
        return ret


    @Url.setter
    def Url(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().PictureShape_set_Url.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().PictureShape_set_Url,self.Ptr,valuePtr)

    @property
    def Transparency(self)->int:
        """
    <summary>
        Gets or sets the Transparency of a picture fill.
            The value ranges from 0 to 100.
    </summary>
        """
        GetDllLibPpt().PictureShape_get_Transparency.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Transparency.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PictureShape_get_Transparency,self.Ptr)
        return ret

    @Transparency.setter
    def Transparency(self, value:int):
        GetDllLibPpt().PictureShape_set_Transparency.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PictureShape_set_Transparency,self.Ptr, value)

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a picture.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().PictureShape_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureShape_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().PictureShape_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().PictureShape_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PictureShape_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


