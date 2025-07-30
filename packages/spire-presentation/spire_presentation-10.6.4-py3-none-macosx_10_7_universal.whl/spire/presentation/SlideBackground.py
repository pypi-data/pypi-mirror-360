from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideBackground (  IActiveSlide) :
    """
    <summary>
        Represents background of a slide.
    </summary>
    """
    @property

    def Type(self)->'BackgroundType':
        """
    <summary>
        Gets a type of background fill.
            Read/write <see cref="T:Spire.Presentation.Drawing.BackgroundType" />.
    </summary>
        """
        GetDllLibPpt().SlideBackground_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideBackground_get_Type,self.Ptr)
        objwraped = BackgroundType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'BackgroundType'):
        GetDllLibPpt().SlideBackground_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideBackground_set_Type,self.Ptr, value.value)

    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets Effect Dag.
    </summary>
        """
        GetDllLibPpt().SlideBackground_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets a FillFormat for BackgroundType.OwnBackground fill.
            Readonly <see cref="P:Spire.Presentation.SlideBackground.Fill" />.
    </summary>
        """
        GetDllLibPpt().SlideBackground_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @Fill.setter
    def Fill(self, value:'FillFormat'):
        GetDllLibPpt().SlideBackground_set_Fill.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideBackground_set_Fill,self.Ptr, value.Ptr)

    @property

    def ThemeColor(self)->'ColorFormat':
        """
    <summary>
        Return a ColorFormat for Themed fill.
            Readonly <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().SlideBackground_get_ThemeColor.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_ThemeColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_ThemeColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @ThemeColor.setter
    def ThemeColor(self, value:'ColorFormat'):
        GetDllLibPpt().SlideBackground_set_ThemeColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideBackground_set_ThemeColor,self.Ptr, value.Ptr)

    @property

    def ThemeIndex(self)->'UInt16':
        """
    <summary>
        Gets an index of Theme.
            0..999, 0 eqauls no fill.
    </summary>
        """
        GetDllLibPpt().SlideBackground_get_ThemeIndex.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_ThemeIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_ThemeIndex,self.Ptr)
        ret = None if intPtr==None else UInt16(intPtr)
        return ret


    @ThemeIndex.setter
    def ThemeIndex(self, value:'UInt16'):
        GetDllLibPpt().SlideBackground_set_ThemeIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideBackground_set_ThemeIndex,self.Ptr, value.Ptr)


    def GetBackgroundFillFormat(self ,slide:'ActiveSlide')->'FillFormat':
        """
    <summary>
        Gets slide's background fillformat.
            Read only <see cref="M:Spire.Presentation.SlideBackground.GetBackgroundFillFormat(Spire.Presentation.ActiveSlide)" />.
    </summary>
    <param name="slide">the slide with current background.</param>
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideBackground_GetBackgroundFillFormat.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideBackground_GetBackgroundFillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_GetBackgroundFillFormat,self.Ptr, intPtrslide)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SlideBackground_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideBackground_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideBackground_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().SlideBackground_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
    <summary>
        Gets the parent presentation of a slide.
            Read-only <see cref="T:Spire.Presentation.PresentationPptx" />.
    </summary>
        """
        GetDllLibPpt().SlideBackground_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


