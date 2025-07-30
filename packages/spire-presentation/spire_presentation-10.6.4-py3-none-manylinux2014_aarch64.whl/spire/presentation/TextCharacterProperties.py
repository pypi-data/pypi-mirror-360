from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from spire.presentation.ClickHyperlink import ClickHyperlink
from ctypes import *
from spire.presentation.TextFont import TextFont

class TextCharacterProperties (  IActiveSlide) :
    """
    <summary>
        Represents a text rane with formatting.
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextCharacterProperties_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextCharacterProperties_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Format(self)->'DefaultTextRangeProperties':
        """
    <summary>
        Gets the text range format for this object.
            Read-only <see cref="T:Spire.Presentation.DefaultTextRangeProperties" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_Format.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Format.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Format,self.Ptr)
        ret = None if intPtr==None else DefaultTextRangeProperties(intPtr)
        return ret


    @property

    def TextLineFormat(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat properties for text outlining.
            Read-only <see cref="P:Spire.Presentation.TextCharacterProperties.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_TextLineFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextLineFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextLineFormat,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets the text FillFormat properties.
            Read-only <see cref="P:Spire.Presentation.TextCharacterProperties.Fill" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def DisplayFill(self)->'FillFormat':
        """
    <summary>
        Gets the text FillFormat properties.
            if textRange FillType is Undefined,display FillFormat properties inherited from the paragraph\textFrame\layoutSlide\master. 
            Read-only
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_DisplayFill.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_DisplayFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_DisplayFill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets the text EffectFormat properties.
            Read-only <see cref="P:Spire.Presentation.TextCharacterProperties.EffectDag" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def HighlightColor(self)->'ColorFormat':
        """
    <summary>
        Gets the color used to highlight a text.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_HighlightColor.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_HighlightColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_HighlightColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def UnderlineFormat(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat properties used to outline underline line.
            Read-only <see cref="P:Spire.Presentation.TextCharacterProperties.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_UnderlineFormat,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def UnderlineFillFormat(self)->'FillFormat':
        """
    <summary>
        Gets the underline line FillFormat properties.
            Read-only <see cref="P:Spire.Presentation.TextCharacterProperties.Fill" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFillFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_UnderlineFillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_UnderlineFillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def BookmarkId(self)->str:
        """
    <summary>
        Gets or sets bookmark identifier.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_BookmarkId.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_BookmarkId.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextCharacterProperties_get_BookmarkId,self.Ptr))
        return ret


    @BookmarkId.setter
    def BookmarkId(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextCharacterProperties_set_BookmarkId.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_BookmarkId,self.Ptr,valuePtr)

    @property
    def HasClickAction(self)->bool:
        """
    <summary>
        Indicates whether text character properties a  has clickAction.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_HasClickAction.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_HasClickAction.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_HasClickAction,self.Ptr)
        return ret

    @property

    def ClickAction(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse click.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_ClickAction.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_ClickAction.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_ClickAction,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @ClickAction.setter
    def ClickAction(self, value:'ClickHyperlink'):
        GetDllLibPpt().TextCharacterProperties_set_ClickAction.argtypes=[c_void_p, c_void_p]
        if(value == None):
            CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ClickAction,self.Ptr, None)
        else:
            CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ClickAction,self.Ptr, value.Ptr)

    @property

    def MouseOverAction(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse over.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_MouseOverAction.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_MouseOverAction.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_MouseOverAction,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOverAction.setter
    def MouseOverAction(self, value:'ClickHyperlink'):
        GetDllLibPpt().TextCharacterProperties_set_MouseOverAction.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_MouseOverAction,self.Ptr, value.Ptr)

    @property

    def IsBold(self)->'TriState':
        """
    <summary>
        Indicates whether the font is bold.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_IsBold.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_IsBold.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_IsBold,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsBold.setter
    def IsBold(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_IsBold.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_IsBold,self.Ptr, value.value)

    @property

    def IsItalic(self)->'TriState':
        """
    <summary>
        Indicates whether the font is itallic.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_IsItalic.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_IsItalic.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_IsItalic,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsItalic.setter
    def IsItalic(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_IsItalic.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_IsItalic,self.Ptr, value.value)

    @property

    def Kumimoji(self)->'TriState':
        """
    <summary>
        Indicates whether use eastern language-specific vertical text layout.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_Kumimoji.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Kumimoji.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Kumimoji,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @Kumimoji.setter
    def Kumimoji(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_Kumimoji.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_Kumimoji,self.Ptr, value.value)

    @property

    def NormalizeHeights(self)->'TriState':
        """
    <summary>
        Indicates whether the height of a text should be normalized.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_NormalizeHeights.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_NormalizeHeights.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_NormalizeHeights,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @NormalizeHeights.setter
    def NormalizeHeights(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_NormalizeHeights.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_NormalizeHeights,self.Ptr, value.value)

    @property

    def NoProofing(self)->'TriState':
        """
    <summary>
        Indicates whether the text would be proofed.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_NoProofing.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_NoProofing.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_NoProofing,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @NoProofing.setter
    def NoProofing(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_NoProofing.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_NoProofing,self.Ptr, value.value)

    @property

    def TextUnderlineType(self)->'TextUnderlineType':
        """
    <summary>
        Gets or sets the text underline type.
            Read/write <see cref="T:Spire.Presentation.TextUnderlineType" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_TextUnderlineType.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextUnderlineType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextUnderlineType,self.Ptr)
        objwraped = TextUnderlineType(ret)
        return objwraped

    @TextUnderlineType.setter
    def TextUnderlineType(self, value:'TextUnderlineType'):
        GetDllLibPpt().TextCharacterProperties_set_TextUnderlineType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_TextUnderlineType,self.Ptr, value.value)

    @property

    def TextCapType(self)->'TextCapType':
        """
    <summary>
        Gets or sets the type of text capitalization.
            Read/write <see cref="T:Spire.Presentation.TextCapType" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_TextCapType.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextCapType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextCapType,self.Ptr)
        objwraped = TextCapType(ret)
        return objwraped

    @TextCapType.setter
    def TextCapType(self, value:'TextCapType'):
        GetDllLibPpt().TextCharacterProperties_set_TextCapType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_TextCapType,self.Ptr, value.value)

    @property

    def TextStrikethroughType(self)->'TextStrikethroughType':
        """
    <summary>
        Gets or sets the strikethrough type of a text.
            Read/write <see cref="T:Spire.Presentation.TextStrikethroughType" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_TextStrikethroughType.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_TextStrikethroughType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_TextStrikethroughType,self.Ptr)
        objwraped = TextStrikethroughType(ret)
        return objwraped

    @TextStrikethroughType.setter
    def TextStrikethroughType(self, value:'TextStrikethroughType'):
        GetDllLibPpt().TextCharacterProperties_set_TextStrikethroughType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_TextStrikethroughType,self.Ptr, value.value)

    @property
    def SmartTagClean(self)->bool:
        """
    <summary>
        Indicates whether the smart tag should be cleaned.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_SmartTagClean.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_SmartTagClean.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_SmartTagClean,self.Ptr)
        return ret

    @SmartTagClean.setter
    def SmartTagClean(self, value:bool):
        GetDllLibPpt().TextCharacterProperties_set_SmartTagClean.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_SmartTagClean,self.Ptr, value)

    @property

    def IsInheritUnderlineFill(self)->'TriState':
        """

        """
        GetDllLibPpt().TextCharacterProperties_get_IsInheritUnderlineFill.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_IsInheritUnderlineFill.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_IsInheritUnderlineFill,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsInheritUnderlineFill.setter
    def IsInheritUnderlineFill(self, value:'TriState'):
        GetDllLibPpt().TextCharacterProperties_set_IsInheritUnderlineFill.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_IsInheritUnderlineFill,self.Ptr, value.value)

    @property
    def FontHeight(self)->float:
        """
    <summary>
        Gets or sets the font height of a text range.
            Read/write <see cref="T:System.Int16" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_FontHeight.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_FontHeight.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_FontHeight,self.Ptr)
        return ret

    @FontHeight.setter
    def FontHeight(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_FontHeight.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_FontHeight,self.Ptr, value)

    @property

    def LatinFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the Latin font info.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_LatinFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_LatinFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_LatinFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @LatinFont.setter
    def LatinFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_LatinFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_LatinFont,self.Ptr, value.Ptr)

    @property

    def DefaultLatinFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the DefaultLatin font info.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_DefaultLatinFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_DefaultLatinFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_DefaultLatinFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @DefaultLatinFont.setter
    def DefaultLatinFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_DefaultLatinFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_DefaultLatinFont,self.Ptr, value.Ptr)

    @property

    def EastAsianFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the East Asian font info.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_EastAsianFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_EastAsianFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_EastAsianFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @EastAsianFont.setter
    def EastAsianFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_EastAsianFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_EastAsianFont,self.Ptr, value.Ptr)

    @property

    def ComplexScriptFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the complex script font info.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_ComplexScriptFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_ComplexScriptFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_ComplexScriptFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @ComplexScriptFont.setter
    def ComplexScriptFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_ComplexScriptFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ComplexScriptFont,self.Ptr, value.Ptr)

    @property

    def SymbolFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the symbolic font info.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_SymbolFont.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_SymbolFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_SymbolFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @SymbolFont.setter
    def SymbolFont(self, value:'TextFont'):
        GetDllLibPpt().TextCharacterProperties_set_SymbolFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_SymbolFont,self.Ptr, value.Ptr)

    @property
    def ScriptDistance(self)->float:
        """
    <summary>
        Gets or sets the superscript or subscript text.
            Read/write <see cref="T:System.Int16" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_ScriptDistance.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_ScriptDistance.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_ScriptDistance,self.Ptr)
        return ret

    @ScriptDistance.setter
    def ScriptDistance(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_ScriptDistance.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_ScriptDistance,self.Ptr, value)

    @property
    def FontMinSize(self)->float:
        """
    <summary>
        Gets or sets the minimal font size.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_FontMinSize.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_FontMinSize.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_FontMinSize,self.Ptr)
        return ret

    @FontMinSize.setter
    def FontMinSize(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_FontMinSize.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_FontMinSize,self.Ptr, value)

    @property

    def Language(self)->str:
        """
    <summary>
        Gets or sets the  language.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_Language.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_Language.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextCharacterProperties_get_Language,self.Ptr))
        return ret


    @Language.setter
    def Language(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextCharacterProperties_set_Language.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_Language,self.Ptr,valuePtr)

    @property

    def AlternativeLanguage(self)->str:
        """
    <summary>
        Gets or sets the alternative language.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_AlternativeLanguage.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_AlternativeLanguage.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextCharacterProperties_get_AlternativeLanguage,self.Ptr))
        return ret


    @AlternativeLanguage.setter
    def AlternativeLanguage(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextCharacterProperties_set_AlternativeLanguage.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_AlternativeLanguage,self.Ptr,valuePtr)

    @property
    def LineSpacing(self)->float:
        """
    <summary>
        Gets or sets the line spacing.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().TextCharacterProperties_get_LineSpacing.argtypes=[c_void_p]
        GetDllLibPpt().TextCharacterProperties_get_LineSpacing.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TextCharacterProperties_get_LineSpacing,self.Ptr)
        return ret

    @LineSpacing.setter
    def LineSpacing(self, value:float):
        GetDllLibPpt().TextCharacterProperties_set_LineSpacing.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TextCharacterProperties_set_LineSpacing,self.Ptr, value)

