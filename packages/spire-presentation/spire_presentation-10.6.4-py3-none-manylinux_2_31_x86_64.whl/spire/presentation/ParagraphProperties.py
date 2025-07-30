from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ParagraphProperties (  PptObject, IActiveSlide) :
    """
    <summary>
        Represents the properties of a paragraph.
    </summary>
    """
    @property

    def Depth(self)->'int':
        """
    <summary>
        Gets or sets a depth of a paragraph.
            Read/write <see cref="T:System.Int16" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_Depth.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Depth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Depth,self.Ptr)
        return ret


    @Depth.setter
    def Depth(self, value:'int'):
        GetDllLibPpt().ParagraphProperties_set_Depth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_Depth,self.Ptr, value)

    @property

    def BulletType(self)->'TextBulletType':
        """
    <summary>
        Gets or sets the bullet type of a paragraph.
            Read/write <see cref="T:Spire.Presentation.TextBulletType" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletType.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletType,self.Ptr)
        objwraped = TextBulletType(ret)
        return objwraped

    @BulletType.setter
    def BulletType(self, value:'TextBulletType'):
        GetDllLibPpt().ParagraphProperties_set_BulletType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletType,self.Ptr, value.value)

    @property
    def BulletChar(self)->int:
        """
    <summary>
        Gets or sets the bullet char of a paragraph.
            Read/write <see cref="T:System.Char" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletChar.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletChar.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletChar,self.Ptr)
        return ret

    @BulletChar.setter
    def BulletChar(self, value:int):
        GetDllLibPpt().ParagraphProperties_set_BulletChar.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletChar,self.Ptr, value)

    @property

    def BulletFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the bullet font of a paragraph.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletFont.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @BulletFont.setter
    def BulletFont(self, value:'TextFont'):
        GetDllLibPpt().ParagraphProperties_set_BulletFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletFont,self.Ptr, value.Ptr)

    @property
    def BulletSize(self)->float:
        """
    <summary>
        Gets or sets the bullet size of a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletSize.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletSize,self.Ptr)
        return ret

    @BulletSize.setter
    def BulletSize(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_BulletSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletSize,self.Ptr, value)

    @property

    def ParagraphBulletColor(self)->'ColorFormat':
        """
    <summary>
        Gets the color format of a bullet of a paragraph.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_ParagraphBulletColor.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_ParagraphBulletColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_ParagraphBulletColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def BulletNumber(self)->'int':
        """
    <summary>
        Gets or sets the first number which is used for group of numbered bullets.
            Read/write <see cref="T:System.Int16" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletNumber.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletNumber.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletNumber,self.Ptr)
        return ret


    @BulletNumber.setter
    def BulletNumber(self, value:'int'):
        GetDllLibPpt().ParagraphProperties_set_BulletNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletNumber,self.Ptr, value)

    @property

    def BulletStyle(self)->'NumberedBulletStyle':
        """
    <summary>
        Gets or sets the style of a numbered bullet.
            Read/write <see cref="T:Spire.Presentation.NumberedBulletStyle" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletStyle.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletStyle,self.Ptr)
        objwraped = NumberedBulletStyle(ret)
        return objwraped

    @BulletStyle.setter
    def BulletStyle(self, value:'NumberedBulletStyle'):
        GetDllLibPpt().ParagraphProperties_set_BulletStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_BulletStyle,self.Ptr, value.value)

    @property

    def Alignment(self)->'TextAlignmentType':
        """
    <summary>
        Gets or sets the text alignment in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TextAlignmentType" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Alignment,self.Ptr)
        objwraped = TextAlignmentType(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'TextAlignmentType'):
        GetDllLibPpt().ParagraphProperties_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_Alignment,self.Ptr, value.value)

    @property
    def LineSpacing(self)->float:
        """
    <summary>
        Gets or sets the amount of space between base lines in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_LineSpacing.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_LineSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_LineSpacing,self.Ptr)
        return ret

    @LineSpacing.setter
    def LineSpacing(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_LineSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_LineSpacing,self.Ptr, value)

    @property
    def SpaceBefore(self)->float:
        """
    <summary>
        Returns or sets the amount of space before the first line in each paragraph of the specified text, in points or lines
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_SpaceBefore.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_SpaceBefore.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_SpaceBefore,self.Ptr)
        return ret

    @SpaceBefore.setter
    def SpaceBefore(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_SpaceBefore.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_SpaceBefore,self.Ptr, value)

    @property
    def SpaceAfter(self)->float:
        """
    <summary>
        Returns or sets the amount of space after the last line in each paragraph of the specified text, in points or lines. 
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_SpaceAfter.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_SpaceAfter.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_SpaceAfter,self.Ptr)
        return ret

    @SpaceAfter.setter
    def SpaceAfter(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_SpaceAfter.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_SpaceAfter,self.Ptr, value)

    @property

    def EastAsianLineBreak(self)->'TriState':
        """
    <summary>
        Indicates whether the East Asian line break is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_EastAsianLineBreak.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_EastAsianLineBreak.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_EastAsianLineBreak,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @EastAsianLineBreak.setter
    def EastAsianLineBreak(self, value:'TriState'):
        GetDllLibPpt().ParagraphProperties_set_EastAsianLineBreak.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_EastAsianLineBreak,self.Ptr, value.value)

    @property

    def RightToLeft(self)->'TriState':
        """
    <summary>
        Indicates whether the Right to Left writing is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_RightToLeft.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_RightToLeft.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_RightToLeft,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RightToLeft.setter
    def RightToLeft(self, value:'TriState'):
        GetDllLibPpt().ParagraphProperties_set_RightToLeft.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_RightToLeft,self.Ptr, value.value)

    @property

    def LatinLineBreak(self)->'TriState':
        """
    <summary>
        Indicates whether the Latin line break is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_LatinLineBreak.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_LatinLineBreak.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_LatinLineBreak,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @LatinLineBreak.setter
    def LatinLineBreak(self, value:'TriState'):
        GetDllLibPpt().ParagraphProperties_set_LatinLineBreak.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_LatinLineBreak,self.Ptr, value.value)

    @property

    def HangingPunctuation(self)->'TriState':
        """
    <summary>
        Indicates whether the hanging punctuation is used in a paragraph.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_HangingPunctuation.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_HangingPunctuation.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_HangingPunctuation,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @HangingPunctuation.setter
    def HangingPunctuation(self, value:'TriState'):
        GetDllLibPpt().ParagraphProperties_set_HangingPunctuation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_HangingPunctuation,self.Ptr, value.value)

    @property
    def LeftMargin(self)->float:
        """
    <summary>
        Gets or sets the left margin in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_LeftMargin.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_LeftMargin.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_LeftMargin,self.Ptr)
        return ret

    @LeftMargin.setter
    def LeftMargin(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_LeftMargin.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_LeftMargin,self.Ptr, value)

    @property
    def RightMargin(self)->float:
        """
    <summary>
        Gets or sets the right margin in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_RightMargin.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_RightMargin.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_RightMargin,self.Ptr)
        return ret

    @RightMargin.setter
    def RightMargin(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_RightMargin.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_RightMargin,self.Ptr, value)

    @property
    def Indent(self)->float:
        """
    <summary>
        Gets or sets text indentation in a paragraph.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_Indent.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Indent.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Indent,self.Ptr)
        return ret

    @Indent.setter
    def Indent(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_Indent.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_Indent,self.Ptr, value)

    @property
    def DefaultTabSize(self)->float:
        """
    <summary>
        Gets or sets default tabulation size.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_DefaultTabSize.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_DefaultTabSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_DefaultTabSize,self.Ptr)
        return ret

    @DefaultTabSize.setter
    def DefaultTabSize(self, value:float):
        GetDllLibPpt().ParagraphProperties_set_DefaultTabSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_DefaultTabSize,self.Ptr, value)

    @property

    def Tabs(self)->'TabStopCollection':
        """
    <summary>
        Gets tabulations of a paragraph.
            Read-only <see cref="T:Spire.Presentation.Collections.TabStopCollection" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_Tabs.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_Tabs.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_Tabs,self.Ptr)
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
        GetDllLibPpt().ParagraphProperties_get_FontAlignment.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_FontAlignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_FontAlignment,self.Ptr)
        objwraped = FontAlignmentType(ret)
        return objwraped

    @FontAlignment.setter
    def FontAlignment(self, value:'FontAlignmentType'):
        GetDllLibPpt().ParagraphProperties_set_FontAlignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_FontAlignment,self.Ptr, value.value)

    @property

    def BulletPicture(self)->'PictureShape':
        """
    <summary>
        Gets a Picture used as a bullet in a paragraph.
            Read-only <see cref="T:Spire.Presentation.PictureShape" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletPicture.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletPicture.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletPicture,self.Ptr)
        ret = None if intPtr==None else PictureShape(intPtr)
        return ret


    @property

    def DefaultCharacterProperties(self)->'TextCharacterProperties':
        """
    <summary>
        Gets default character properties of a paragraph.
            Read-only <see cref="T:Spire.Presentation.TextCharacterProperties" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_DefaultCharacterProperties.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_DefaultCharacterProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_DefaultCharacterProperties,self.Ptr)
        ret = None if intPtr==None else TextCharacterProperties(intPtr)
        return ret


    @property
    def HasBullet(self)->bool:
        """
    <summary>
        Indicates whether a paragraph has a bullet.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_HasBullet.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_HasBullet.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_HasBullet,self.Ptr)
        return ret

    @property
    def CustomBulletColor(self)->bool:
        """

        """
        GetDllLibPpt().ParagraphProperties_get_CustomBulletColor.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_CustomBulletColor.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_CustomBulletColor,self.Ptr)
        return ret

    @CustomBulletColor.setter
    def CustomBulletColor(self, value:bool):
        GetDllLibPpt().ParagraphProperties_set_CustomBulletColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_CustomBulletColor,self.Ptr, value)

    @property

    def BulletColor(self)->'ColorFormat':
        """
    <summary>
        Gets or sets the color of a bullet.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().ParagraphProperties_get_BulletColor.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_BulletColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphProperties_get_BulletColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property
    def CustomBulletFont(self)->bool:
        """

        """
        GetDllLibPpt().ParagraphProperties_get_CustomBulletFont.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphProperties_get_CustomBulletFont.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_get_CustomBulletFont,self.Ptr)
        return ret

    @CustomBulletFont.setter
    def CustomBulletFont(self, value:bool):
        GetDllLibPpt().ParagraphProperties_set_CustomBulletFont.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ParagraphProperties_set_CustomBulletFont,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ParagraphProperties_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphProperties_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphProperties_Equals,self.Ptr, intPtrobj)
        return ret

