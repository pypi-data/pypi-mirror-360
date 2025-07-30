from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextParagraphProperties (  IActiveSlide, IActivePresentation) :
    """
    <summary>
        Contains the paragraph's formatting properties.
    </summary>
    """
    @property

    def Level(self)->'Int16':
        """
    <summary>
        Gets or sets a level of a paragraph.
            Read/write <see cref="T:System.Int16" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_Level.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_Level.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_Level,self.Ptr)
        ret = None if intPtr==None else Int16(intPtr)
        return ret


    @Level.setter
    def Level(self, value:'Int16'):
        GetDllLibPpt().TextParagraphProperties_set_Level.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_Level,self.Ptr, value.Ptr)

    @property

    def TextTextBulletType(self)->'TextBulletType':
        """
    <summary>
        Gets or sets the bullet type of a paragraph.
            Read/write <see cref="T:Spire.Presentation.TextBulletType" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_TextTextBulletType.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_TextTextBulletType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_TextTextBulletType,self.Ptr)
        objwraped = TextBulletType(ret)
        return objwraped

    @TextTextBulletType.setter
    def TextTextBulletType(self, value:'TextBulletType'):
        GetDllLibPpt().TextParagraphProperties_set_TextTextBulletType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_TextTextBulletType,self.Ptr, value.value)

    @property
    def BulletChar(self)->int:
        """
    <summary>
        Gets or sets the bullet char of a paragraph.
            Read/write <see cref="T:System.Char" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_BulletChar.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_BulletChar.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_BulletChar,self.Ptr)
        return ret

    @BulletChar.setter
    def BulletChar(self, value:int):
        GetDllLibPpt().TextParagraphProperties_set_BulletChar.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_BulletChar,self.Ptr, value)

    @property

    def BulletFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the bullet font of a paragraph.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_BulletFont.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_BulletFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_BulletFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @BulletFont.setter
    def BulletFont(self, value:'TextFont'):
        GetDllLibPpt().TextParagraphProperties_set_BulletFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_BulletFont,self.Ptr, value.Ptr)

    @property
    def BulletSize(self)->float:
        """
    <summary>
        Gets or sets the bullet height of a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_BulletSize.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_BulletSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_BulletSize,self.Ptr)
        return ret

    @BulletSize.setter
    def BulletSize(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_BulletSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_BulletSize,self.Ptr, value)

    @property

    def BulletColor(self)->'ColorFormat':
        """
    <summary>
        Gets the color format of a bullet of a paragraph.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_BulletColor.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_BulletColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_BulletColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def NumberedBulletStartWith(self)->'Int16':
        """
    <summary>
        Gets or sets the first number which is used for group of numbered bullets.
            Read/write <see cref="T:System.Int16" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_NumberedBulletStartWith.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_NumberedBulletStartWith.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_NumberedBulletStartWith,self.Ptr)
        ret = None if intPtr==None else Int16(intPtr)
        return ret


    @NumberedBulletStartWith.setter
    def NumberedBulletStartWith(self, value:'Int16'):
        GetDllLibPpt().TextParagraphProperties_set_NumberedBulletStartWith.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_NumberedBulletStartWith,self.Ptr, value.Ptr)

    @property

    def NumberedBulletStyle(self)->'NumberedBulletStyle':
        """
    <summary>
        Gets or sets the style of a numbered bullet.
            Read/write <see cref="T:Spire.Presentation.NumberedBulletStyle" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_NumberedBulletStyle.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_NumberedBulletStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_NumberedBulletStyle,self.Ptr)
        objwraped = NumberedBulletStyle(ret)
        return objwraped

    @NumberedBulletStyle.setter
    def NumberedBulletStyle(self, value:'NumberedBulletStyle'):
        GetDllLibPpt().TextParagraphProperties_set_NumberedBulletStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_NumberedBulletStyle,self.Ptr, value.value)

    @property

    def Alignment(self)->'TextAlignmentType':
        """
    <summary>
        Gets or sets the text alignment in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TextAlignmentType" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_Alignment,self.Ptr)
        objwraped = TextAlignmentType(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'TextAlignmentType'):
        GetDllLibPpt().TextParagraphProperties_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_Alignment,self.Ptr, value.value)

    @property
    def LineSpacing(self)->float:
        """
    <summary>
        Gets or sets the amount of space between base lines in a paragraph. Positive value means percentage, negative - size in points.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_LineSpacing.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_LineSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_LineSpacing,self.Ptr)
        return ret

    @LineSpacing.setter
    def LineSpacing(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_LineSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_LineSpacing,self.Ptr, value)

    @property
    def SpaceBefore(self)->float:
        """
    <summary>
        Gets or sets the amount of space before the first line in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_SpaceBefore.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_SpaceBefore.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_SpaceBefore,self.Ptr)
        return ret

    @SpaceBefore.setter
    def SpaceBefore(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_SpaceBefore.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_SpaceBefore,self.Ptr, value)

    @property
    def SpaceAfter(self)->float:
        """
    <summary>
        Gets or sets the amount of space after the last line in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_SpaceAfter.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_SpaceAfter.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_SpaceAfter,self.Ptr)
        return ret

    @SpaceAfter.setter
    def SpaceAfter(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_SpaceAfter.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_SpaceAfter,self.Ptr, value)

    @property

    def EastAsianLineBreak(self)->'TriState':
        """
    <summary>
        Indicates whether the East Asian line break is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_EastAsianLineBreak.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_EastAsianLineBreak.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_EastAsianLineBreak,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @EastAsianLineBreak.setter
    def EastAsianLineBreak(self, value:'TriState'):
        GetDllLibPpt().TextParagraphProperties_set_EastAsianLineBreak.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_EastAsianLineBreak,self.Ptr, value.value)

    @property

    def RightToLeft(self)->'TriState':
        """
    <summary>
        Indicates whether the Right to Left writing is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_RightToLeft.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_RightToLeft.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_RightToLeft,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RightToLeft.setter
    def RightToLeft(self, value:'TriState'):
        GetDllLibPpt().TextParagraphProperties_set_RightToLeft.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_RightToLeft,self.Ptr, value.value)

    @property

    def LatinLineBreak(self)->'TriState':
        """
    <summary>
        Indicates whether the Latin line break is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_LatinLineBreak.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_LatinLineBreak.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_LatinLineBreak,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @LatinLineBreak.setter
    def LatinLineBreak(self, value:'TriState'):
        GetDllLibPpt().TextParagraphProperties_set_LatinLineBreak.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_LatinLineBreak,self.Ptr, value.value)

    @property

    def HangingPunctuation(self)->'TriState':
        """
    <summary>
        Indicates whether the hanging punctuation is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_HangingPunctuation.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_HangingPunctuation.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_HangingPunctuation,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @HangingPunctuation.setter
    def HangingPunctuation(self, value:'TriState'):
        GetDllLibPpt().TextParagraphProperties_set_HangingPunctuation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_HangingPunctuation,self.Ptr, value.value)

    @property
    def LeftMargin(self)->float:
        """
    <summary>
        Gets or sets the left margin in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_LeftMargin.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_LeftMargin.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_LeftMargin,self.Ptr)
        return ret

    @LeftMargin.setter
    def LeftMargin(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_LeftMargin.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_LeftMargin,self.Ptr, value)

    @property
    def RightMargin(self)->float:
        """
    <summary>
        Gets or sets the right margin in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_RightMargin.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_RightMargin.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_RightMargin,self.Ptr)
        return ret

    @RightMargin.setter
    def RightMargin(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_RightMargin.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_RightMargin,self.Ptr, value)

    @property
    def Indent(self)->float:
        """
    <summary>
        Gets or sets text indentation in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_Indent.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_Indent.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_Indent,self.Ptr)
        return ret

    @Indent.setter
    def Indent(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_Indent.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_Indent,self.Ptr, value)

    @property
    def DefaultTabSize(self)->float:
        """
    <summary>
        Gets or sets default tabulation size.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_DefaultTabSize.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_DefaultTabSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_DefaultTabSize,self.Ptr)
        return ret

    @DefaultTabSize.setter
    def DefaultTabSize(self, value:float):
        GetDllLibPpt().TextParagraphProperties_set_DefaultTabSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_DefaultTabSize,self.Ptr, value)

    @property

    def TabStopsList(self)->'TabStopCollection':
        """
    <summary>
        Gets tabulations of a paragraph.
            Read-only <see cref="T:Spire.Presentation.Collections.TabStopCollection" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_TabStopsList.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_TabStopsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_TabStopsList,self.Ptr)
        ret = None if intPtr==None else TabStopCollection(intPtr)
        return ret


    @property

    def FontAlignment(self)->'FontAlignmentType':
        """
    <summary>
        Gets or sets a font alignment in a paragraph.
            Read/write <see cref="T:Spire.Presentation.FontAlignmentType" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_FontAlignment.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_FontAlignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_FontAlignment,self.Ptr)
        objwraped = FontAlignmentType(ret)
        return objwraped

    @FontAlignment.setter
    def FontAlignment(self, value:'FontAlignmentType'):
        GetDllLibPpt().TextParagraphProperties_set_FontAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_FontAlignment,self.Ptr, value.value)

    @property

    def DefaultTextRangeProperties(self)->'DefaultTextRangeProperties':
        """
    <summary>
        Gets default portion format of a paragraph.
            Read-only <see cref="P:Spire.Presentation.TextParagraphProperties.DefaultTextRangeProperties" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_DefaultTextRangeProperties.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_DefaultTextRangeProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_DefaultTextRangeProperties,self.Ptr)
        ret = None if intPtr==None else DefaultTextRangeProperties(intPtr)
        return ret


    @property
    def CustomBulletColor(self)->bool:
        """

        """
        GetDllLibPpt().TextParagraphProperties_get_CustomBulletColor.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_CustomBulletColor.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_CustomBulletColor,self.Ptr)
        return ret

    @CustomBulletColor.setter
    def CustomBulletColor(self, value:bool):
        GetDllLibPpt().TextParagraphProperties_set_CustomBulletColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_CustomBulletColor,self.Ptr, value)

    @property

    def IsBulletInheritFont(self)->'TriState':
        """
    <summary>
        Indicates whether the bullet has own font or inherits it from the first portion in the paragraph.
            <b>NullableBool.True</b> if bullet has own font and <b>NullableBool.False</b> if bullet
            inherits font from the first portion in the paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextParagraphProperties_get_IsBulletInheritFont.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraphProperties_get_IsBulletInheritFont.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_get_IsBulletInheritFont,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsBulletInheritFont.setter
    def IsBulletInheritFont(self, value:'TriState'):
        GetDllLibPpt().TextParagraphProperties_set_IsBulletInheritFont.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextParagraphProperties_set_IsBulletInheritFont,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextParagraphProperties_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextParagraphProperties_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextParagraphProperties_Equals,self.Ptr, intPtrobj)
        return ret

