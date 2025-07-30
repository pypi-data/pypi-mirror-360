from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MasterTheme (  Theme) :
    """
    <summary>
        Represents a master theme.
    </summary>
    """
    @property

    def ColorScheme(self)->'ColorScheme':
        """
    <summary>
        Gets the color scheme.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorScheme" />.
    </summary>
        """
        GetDllLibPpt().MasterTheme_get_ColorScheme.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_ColorScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_ColorScheme,self.Ptr)
        ret = None if intPtr==None else ColorScheme(intPtr)
        return ret


    @property

    def FontScheme(self)->'FontScheme':
        """
    <summary>
        Gets the font scheme.
            Read-only <see cref="T:Spire.Presentation.FontScheme" />.
    </summary>
        """
        GetDllLibPpt().MasterTheme_get_FontScheme.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_FontScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_FontScheme,self.Ptr)
        ret = None if intPtr==None else FontScheme(intPtr)
        return ret


    @property

    def FormatScheme(self)->'FormatScheme':
        """
    <summary>
        Gets the shape format scheme.
            Read-only <see cref="T:Spire.Presentation.Drawing.FormatScheme" />.
    </summary>
        """
        GetDllLibPpt().MasterTheme_get_FormatScheme.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_FormatScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_FormatScheme,self.Ptr)
        ret = None if intPtr==None else FormatScheme(intPtr)
        return ret


    @property

    def SlideColorSchemes(self)->'SlideColorSchemeCollection':
        """
    <summary>
        Gets the collection of additional color schemes.
            These schemes don't affect presentation's look, they can be selected as main color scheme for a slide.
            Read-only <see cref="T:Spire.Presentation.Collections.SlideColorSchemeCollection" />.
    </summary>
        """
        GetDllLibPpt().MasterTheme_get_SlideColorSchemes.argtypes=[c_void_p]
        GetDllLibPpt().MasterTheme_get_SlideColorSchemes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MasterTheme_get_SlideColorSchemes,self.Ptr)
        ret = None if intPtr==None else SlideColorSchemeCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().MasterTheme_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().MasterTheme_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().MasterTheme_Equals,self.Ptr, intPtrobj)
        return ret

