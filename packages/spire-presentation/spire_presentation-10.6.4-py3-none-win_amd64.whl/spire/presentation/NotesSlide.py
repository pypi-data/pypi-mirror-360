from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class NotesSlide (  ActiveSlide) :
    """
    <summary>
        Represents a notes slide in a presentation.
    </summary>
    """
    @property

    def NotesTextFrame(self)->'ITextFrameProperties':
        """
    <summary>
        Gets a TextFrame with notes' text if there is one.
            Readonly <see cref="T:Spire.Presentation.TextFrameProperties" />.
    </summary>
        """
        GetDllLibPpt().NotesSlide_get_NotesTextFrame.argtypes=[c_void_p]
        GetDllLibPpt().NotesSlide_get_NotesTextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().NotesSlide_get_NotesTextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Theme(self)->'Theme':
        """
    <summary>
        Gets the theme object from master.
    </summary>
        """
        GetDllLibPpt().NotesSlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().NotesSlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().NotesSlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
    <summary>
        Applies extra color scheme to a slide.
    </summary>
    <param name="scheme"></param>
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().NotesSlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().NotesSlide_ApplyTheme,self.Ptr, intPtrscheme)

    #@dispatch

    #def GetThumbnail(self ,scaleX:float,scaleY:float)->Bitmap:
    #    """
    #<summary>
    #    Gets a Thumbnail Bitmap object with custom scaling.
    #</summary>
    #<param name="scaleX">The value by which to scale this Thumbnail in the x-axis direction.</param>
    #<param name="scaleY">The value by which to scale this Thumbnail in the y-axis direction.</param>
    #<returns>Bitmap object.</returns>
    #    """
        
    #    GetDllLibPpt().NotesSlide_GetThumbnail.argtypes=[c_void_p ,c_float,c_float]
    #    GetDllLibPpt().NotesSlide_GetThumbnail.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().NotesSlide_GetThumbnail,self.Ptr, scaleX,scaleY)
    #    ret = None if intPtr==None else Bitmap(intPtr)
    #    return ret


    #@dispatch

    #def GetThumbnail(self ,imageSize:Size)->Bitmap:
    #    """
    #<summary>
    #    Gets a Thumbnail Bitmap object with specified size.
    #</summary>
    #<param name="imageSize">Size of the image to create.</param>
    #<returns>Bitmap object.</returns>
    #    """
    #    intPtrimageSize:c_void_p = imageSize.Ptr

    #    GetDllLibPpt().NotesSlide_GetThumbnailI.argtypes=[c_void_p ,c_void_p]
    #    GetDllLibPpt().NotesSlide_GetThumbnailI.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().NotesSlide_GetThumbnailI,self.Ptr, intPtrimageSize)
    #    ret = None if intPtr==None else Bitmap(intPtr)
    #    return ret


