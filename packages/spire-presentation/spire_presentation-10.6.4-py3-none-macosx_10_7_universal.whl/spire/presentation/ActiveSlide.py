from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ActiveSlide (  PptObject, IActiveSlide) :
    """
    <summary>
         Represents common slide types.
    </summary>
    """
    @property

    def Shapes(self)->'ShapeCollection':
        """
    <summary>
        Gets the shapes of a slide.
            Read-only <see cref="T:Spire.Presentation.ShapeCollection" />.
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the name of a slide.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ActiveSlide_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ActiveSlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ActiveSlide_set_Name,self.Ptr,valuePtr)

    @property

    def SlideID(self)->'int':
        """
    <summary>
        Gets the ID of a slide.
            Read-only <see cref="T:System.UInt32" />.
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_SlideID.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_SlideID.restype=c_void_p
        slidId = CallCFunction(GetDllLibPpt().ActiveSlide_get_SlideID,self.Ptr)
        return slidId


    #@SlideID.setter
    #def SlideID(self, value:'UInt32'):
    #    GetDllLibPpt().ActiveSlide_set_SlideID.argtypes=[c_void_p, c_void_p]
    #    CallCFunction(GetDllLibPpt().ActiveSlide_set_SlideID,self.Ptr, value.Ptr)

    @property

    def Theme(self)->'Theme':
        """
    <summary>
        Gets a theme for this slide
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Theme,self.Ptr)
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

        GetDllLibPpt().ActiveSlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ActiveSlide_ApplyTheme,self.Ptr, intPtrscheme)

    @property

    def TagsList(self)->'TagCollection':
        """
    <summary>
        Gets the slide's tags collection.
            Read-only <see cref="T:Spire.Presentation.Collections.TagCollection" />.
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Timeline(self)->'TimeLine':
        """
    <summary>
        Gets animation timeline object.
            Read-only <see cref="T:Spire.Presentation.Drawing.Animation.TimeLine" />.
    </summary>
        """
        from spire.presentation import TimeLine
        GetDllLibPpt().ActiveSlide_get_Timeline.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Timeline.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Timeline,self.Ptr)
        ret = None if intPtr==None else TimeLine(intPtr)
        return ret


    @property

    def SlideShowTransition(self)->'SlideShowTransition':
        """
    <summary>
        Gets the Transition object which contains information about
            how the specified slide advances during a slide show.
            Read-only <see cref="P:Spire.Presentation.ActiveSlide.SlideShowTransition" />.
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_SlideShowTransition.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_SlideShowTransition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_SlideShowTransition,self.Ptr)
        ret = None if intPtr==None else SlideShowTransition(intPtr)
        return ret


    @property

    def SlideBackground(self)->'SlideBackground':
        """
    <summary>
        Gets slide's background.
            Read only <see cref="P:Spire.Presentation.ActiveSlide.SlideBackground" />.
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_SlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_SlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_SlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def DisplaySlideBackground(self)->'SlideBackground':
        """
    <summary>
        Gets slide's display background.
            Read only <see cref="P:Spire.Presentation.ActiveSlide.DisplaySlideBackground" />.
    </summary>
        """
        GetDllLibPpt().ActiveSlide_get_DisplaySlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_DisplaySlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_DisplaySlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ActiveSlide_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ActiveSlide_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ActiveSlide_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Presentation(self)->'Presentation':
        """

        """
        from spire.presentation import Presentation
        GetDllLibPpt().ActiveSlide_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ActiveSlide_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ActiveSlide_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


