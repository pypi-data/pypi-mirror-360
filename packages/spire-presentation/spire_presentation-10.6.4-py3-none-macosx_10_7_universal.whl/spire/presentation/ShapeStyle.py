from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeStyle (  IActiveSlide, IActivePresentation) :
    """
    <summary>
        Represent shape's style reference.
    </summary>
    """
    @property

    def LineColor(self)->'ColorFormat':
        """
    <summary>
        Gets a shape's outline color.
            Readonly <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_LineColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_LineColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_LineColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def LineStyleIndex(self)->'UInt16':
        """
    <summary>
        Gets or sets line's column index in a style matrix.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_LineStyleIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_LineStyleIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_LineStyleIndex,self.Ptr)
        ret = None if intPtr==None else UInt16(intPtr)
        return ret


    @LineStyleIndex.setter
    def LineStyleIndex(self, value:'UInt16'):
        GetDllLibPpt().ShapeStyle_set_LineStyleIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_LineStyleIndex,self.Ptr, value.Ptr)

    @property

    def FillColor(self)->'ColorFormat':
        """
    <summary>
        Gets a shape's fill color.
            Readonly <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_FillColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FillColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_FillColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def FillStyleIndex(self)->'Int16':
        """
    <summary>
        Gets or sets shape's fill column index in style matrices.
            0 means no fill,
            positive value - index in theme's fill styles,
            negative value - index in theme's background styles.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_FillStyleIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FillStyleIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_FillStyleIndex,self.Ptr)
        ret = None if intPtr==None else Int16(intPtr)
        return ret


    @FillStyleIndex.setter
    def FillStyleIndex(self, value:'Int16'):
        GetDllLibPpt().ShapeStyle_set_FillStyleIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_FillStyleIndex,self.Ptr, value.Ptr)

    @property

    def EffectColor(self)->'ColorFormat':
        """
    <summary>
        Gets a shape's effect color.
            Readonly <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_EffectColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_EffectColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_EffectColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def EffectStyleIndex(self)->'UInt32':
        """
    <summary>
        Gets or sets shape's effect column index in a style matrix.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_EffectStyleIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_EffectStyleIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_EffectStyleIndex,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret


    @EffectStyleIndex.setter
    def EffectStyleIndex(self, value:'UInt32'):
        GetDllLibPpt().ShapeStyle_set_EffectStyleIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_EffectStyleIndex,self.Ptr, value.Ptr)

    @property

    def FontColor(self)->'ColorFormat':
        """
    <summary>
        Gets a shape's font color.
            Readonly <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_FontColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FontColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_FontColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def FontCollectionIndex(self)->'FontCollectionIndex':
        """
    <summary>
        Gets or sets shape's font index in a font collection.
            Read/write <see cref="P:Spire.Presentation.ShapeStyle.FontCollectionIndex" />.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_FontCollectionIndex.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_FontCollectionIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeStyle_get_FontCollectionIndex,self.Ptr)
        objwraped = FontCollectionIndex(ret)
        return objwraped

    @FontCollectionIndex.setter
    def FontCollectionIndex(self, value:'FontCollectionIndex'):
        GetDllLibPpt().ShapeStyle_set_FontCollectionIndex.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeStyle_set_FontCollectionIndex,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeStyle_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeStyle_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeStyle_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape style.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().ShapeStyle_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().ShapeStyle_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ShapeStyle_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeStyle_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


