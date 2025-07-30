from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class INoteMasterSlide (SpireObject) :
    """

    """
    @property

    def Theme(self)->'Theme':
        """
    <summary>
        Gets the slide's theme.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret


    @property

    def Shapes(self)->'ShapeCollection':
        """
    <summary>
        Gets the shapes of a slide.
            Read-only <see cref="T:Spire.Presentation.ShapeCollection" />.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Shapes,self.Ptr)
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
        GetDllLibPpt().INoteMasterSlide_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().INoteMasterSlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().INoteMasterSlide_set_Name,self.Ptr,valuePtr)

    @property

    def SlideID(self)->'UInt32':
        """
    <summary>
        Gets the ID of a slide.
            Read-only <see cref="T:System.UInt32" />.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_get_SlideID.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_SlideID.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_SlideID,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
    <summary>
        Gets the slide's tags collection.
            Read-only <see cref="T:Spire.Presentation.Collections.TagCollection" />.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_TagsList,self.Ptr)
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
        GetDllLibPpt().INoteMasterSlide_get_Timeline.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Timeline.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Timeline,self.Ptr)
        ret = None if intPtr==None else TimeLine(intPtr)
        return ret


    @property

    def SlideShowTransition(self)->'SlideShowTransition':
        """
    <summary>
        Gets the Transition object which contains information about
            how the specified slide advances during a slide show.
            Read-only <see cref="P:Spire.Presentation.INoteMasterSlide.SlideShowTransition" />.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_get_SlideShowTransition.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_SlideShowTransition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_SlideShowTransition,self.Ptr)
        ret = None if intPtr==None else SlideShowTransition(intPtr)
        return ret


    @property

    def SlideBackground(self)->'SlideBackground':
        """
    <summary>
        Gets slide's background.
            Read only <see cref="P:Spire.Presentation.INoteMasterSlide.SlideBackground" />.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_get_SlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_SlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_SlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().INoteMasterSlide_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
    <summary>
        Reference to Parent object. Read-only.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().INoteMasterSlide_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().INoteMasterSlide_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
    <summary>
        Applies extra color scheme to a slide.
    </summary>
    <param name="scheme"></param>
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().INoteMasterSlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().INoteMasterSlide_ApplyTheme,self.Ptr, intPtrscheme)

    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().INoteMasterSlide_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().INoteMasterSlide_Dispose,self.Ptr)

