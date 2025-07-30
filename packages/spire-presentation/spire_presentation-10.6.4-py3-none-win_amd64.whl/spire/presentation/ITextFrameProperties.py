from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITextFrameProperties (SpireObject) :
    """

    """
    @property

    def Paragraphs(self)->'ParagraphCollection':
        """
    <summary>
        Gets the list of all paragraphs in a frame.
            Read-only <see cref="T:Spire.Presentation.Collections.ParagraphCollection" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_Paragraphs.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Paragraphs.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Paragraphs,self.Ptr)
        ret = None if intPtr==None else ParagraphCollection(intPtr)
        return ret


    @property

    def Text(self)->str:
        """
    <summary>
        Gets or sets the plain text for a TextFrame.
    </summary>
<value>
            The text.
            </value>
        """
        GetDllLibPpt().ITextFrameProperties_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Text.restype=c_void_p
        ret =PtrToStr(CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITextFrameProperties_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_Text,self.Ptr,valuePtr)

    @property

    def TextStyle(self)->'TextStyle':
        """
    <summary>
        Gets text's style.
            Readonly <see cref="T:Spire.Presentation.TextStyle" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_TextStyle.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextStyle,self.Ptr)
        ret = None if intPtr==None else TextStyle(intPtr)
        return ret


    @property
    def MarginLeft(self)->float:
        """
    <summary>
        Gets or sets the left margin (points) in a TextFrame.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginLeft.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginLeft.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginLeft,self.Ptr)
        return ret

    @MarginLeft.setter
    def MarginLeft(self, value:float):
        GetDllLibPpt().ITextFrameProperties_set_MarginLeft.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginLeft,self.Ptr, value)

    @property
    def ColumnCount(self)->int:
        """
    <summary>
        Gets or sets the left margin (points) in a TextFrame.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_ColumnCount.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_ColumnCount.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_ColumnCount,self.Ptr)
        return ret

    @ColumnCount.setter
    def ColumnCount(self, value:int):
        GetDllLibPpt().ITextFrameProperties_set_ColumnCount.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_ColumnCount,self.Ptr, value)

    @property
    def ColumnSpacing(self)->float:
        """
    <summary>
        Gets or sets the left margin (points) in a TextFrame.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_ColumnSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_ColumnSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_ColumnSpacing,self.Ptr)
        return ret

    @ColumnSpacing.setter
    def ColumnSpacing(self, value:float):
        GetDllLibPpt().ITextFrameProperties_set_ColumnSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_ColumnSpacing,self.Ptr, value)

    @property
    def MarginRight(self)->float:
        """
    <summary>
        Gets or sets the right margin (points) in a TextFrame.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginRight.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginRight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginRight,self.Ptr)
        return ret

    @MarginRight.setter
    def MarginRight(self, value:float):
        GetDllLibPpt().ITextFrameProperties_set_MarginRight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginRight,self.Ptr, value)

    @property
    def MarginTop(self)->float:
        """
    <summary>
        Gets or sets the top margin (points) in a TextFrame.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginTop.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginTop.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginTop,self.Ptr)
        return ret

    @MarginTop.setter
    def MarginTop(self, value:float):
        GetDllLibPpt().ITextFrameProperties_set_MarginTop.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginTop,self.Ptr, value)

    @property
    def MarginBottom(self)->float:
        """
    <summary>
        Gets or sets the bottom margin (points) in a TextFrame.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_MarginBottom.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_MarginBottom.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_MarginBottom,self.Ptr)
        return ret

    @MarginBottom.setter
    def MarginBottom(self, value:float):
        GetDllLibPpt().ITextFrameProperties_set_MarginBottom.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_MarginBottom,self.Ptr, value)

    @property

    def TextRange(self)->'TextRange':
        """
    <summary>
        Text range of text frame.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_TextRange.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextRange,self.Ptr)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret


    @property
    def WordWrap(self)->bool:
        """
<summary>
  <b>True</b> if text is wrapped at TextFrame's margins.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_WordWrap.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_WordWrap.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_WordWrap,self.Ptr)
        return ret

    @WordWrap.setter
    def WordWrap(self, value:bool):
        GetDllLibPpt().ITextFrameProperties_set_WordWrap.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_WordWrap,self.Ptr, value)

    @property

    def AnchoringType(self)->'TextAnchorType':
        """
    <summary>
        Gets or sets vertical anchor text in a TextFrame.
            Read/write <see cref="T:Spire.Presentation.TextAnchorType" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_AnchoringType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_AnchoringType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_AnchoringType,self.Ptr)
        objwraped = TextAnchorType(ret)
        return objwraped

    @AnchoringType.setter
    def AnchoringType(self, value:'TextAnchorType'):
        GetDllLibPpt().ITextFrameProperties_set_AnchoringType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_AnchoringType,self.Ptr, value.value)

    @property
    def IsCentered(self)->bool:
        """
    <summary>
        Indicates, whether text should be centered in box horizontally.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_IsCentered.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_IsCentered.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_IsCentered,self.Ptr)
        return ret

    @IsCentered.setter
    def IsCentered(self, value:bool):
        GetDllLibPpt().ITextFrameProperties_set_IsCentered.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_IsCentered,self.Ptr, value)

    @property

    def VerticalTextType(self)->'VerticalTextType':
        """
    <summary>
        Indicates text orientation.
            Read/write <see cref="P:Spire.Presentation.ITextFrameProperties.VerticalTextType" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_VerticalTextType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_VerticalTextType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_VerticalTextType,self.Ptr)
        objwraped = VerticalTextType(ret)
        return objwraped

    @VerticalTextType.setter
    def VerticalTextType(self, value:'VerticalTextType'):
        GetDllLibPpt().ITextFrameProperties_set_VerticalTextType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_VerticalTextType,self.Ptr, value.value)

    @property

    def AutofitType(self)->'TextAutofitType':
        """
    <summary>
        Gets or sets text's autofit mode.
            Read/write <see cref="T:Spire.Presentation.TextAutofitType" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_AutofitType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_AutofitType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_AutofitType,self.Ptr)
        objwraped = TextAutofitType(ret)
        return objwraped

    @AutofitType.setter
    def AutofitType(self, value:'TextAutofitType'):
        GetDllLibPpt().ITextFrameProperties_set_AutofitType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_AutofitType,self.Ptr, value.value)

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a TextFrame.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().ITextFrameProperties_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
    <summary>
        Reference to Parent object. Read-only.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_Dispose,self.Ptr)

    @property

    def TextThreeD(self)->'FormatThreeD':
        """
    <summary>
        Gets the FormatThreeD object that 3d effect properties for text.
            Read-only <see cref="T:Spire.Presentation.Drawing.FormatThreeD" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_TextThreeD.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property
    def RotationAngle(self)->float:
        """
    <summary>
        Gets or sets the rotation angle of text frame .
     </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_RotationAngle.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_RotationAngle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_RotationAngle,self.Ptr)
        return ret

    @RotationAngle.setter
    def RotationAngle(self, value:float):
        GetDllLibPpt().ITextFrameProperties_set_RotationAngle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_RotationAngle,self.Ptr, value)


    def HighLightText(self ,text:str,color:'Color',options:'TextHighLightingOptions'):
        """
    <summary>
        Highlight all matches of sample in text frame text using specified color.
    </summary>
    <param name="text">Text sample to highlight</param>
    <param name="color">Highlighting color</param>
    <param name="options">Highlighting options</param>
        """
        intPtrcolor:c_void_p = color.Ptr
        intPtroptions:c_void_p = options.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().ITextFrameProperties_HighLightText.argtypes=[c_void_p ,c_char_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_HighLightText,self.Ptr,textPtr,intPtrcolor,intPtroptions)

    @property
    def RightToLeftColumns(self)->bool:
        """
    <summary>
        columns style right to left.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_RightToLeftColumns.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_RightToLeftColumns.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_RightToLeftColumns,self.Ptr)
        return ret

    @RightToLeftColumns.setter
    def RightToLeftColumns(self, value:bool):
        GetDllLibPpt().ITextFrameProperties_set_RightToLeftColumns.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_RightToLeftColumns,self.Ptr, value)

    @property

    def TextShapeType(self)->'TextShapeType':
        """
    <summary>
        Gets or sets shape type of text.
             Read/write <see cref="P:Spire.Presentation.ITextFrameProperties.TextShapeType" />.
    </summary>
        """
        GetDllLibPpt().ITextFrameProperties_get_TextShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_get_TextShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITextFrameProperties_get_TextShapeType,self.Ptr)
        objwraped = TextShapeType(ret)
        return objwraped

    @TextShapeType.setter
    def TextShapeType(self, value:'TextShapeType'):
        GetDllLibPpt().ITextFrameProperties_set_TextShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITextFrameProperties_set_TextShapeType,self.Ptr, value.value)


    def GetLayoutLines(self)->List['LineText']:
        """

        """
        GetDllLibPpt().ITextFrameProperties_GetLayoutLines.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_GetLayoutLines.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ITextFrameProperties_GetLayoutLines,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, LineText)
        return ret
    

    def GetTextLocation(self)->PointF:
        """

        """
        GetDllLibPpt().ITextFrameProperties_GetTextLocation.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_GetTextLocation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_GetTextLocation,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret
    

    def GetTextSize(self)->SizeF:
        """

        """
        GetDllLibPpt().ITextFrameProperties_GetTextSize.argtypes=[c_void_p]
        GetDllLibPpt().ITextFrameProperties_GetTextSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITextFrameProperties_GetTextSize,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret

