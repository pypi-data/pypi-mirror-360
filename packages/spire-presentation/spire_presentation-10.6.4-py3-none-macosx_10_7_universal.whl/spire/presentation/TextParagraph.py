from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
from spire.presentation.ParagraphProperties import ParagraphProperties
from spire.presentation.TextRangeCollection import TextRangeCollection

class TextParagraph (  ParagraphProperties) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().TextParagraph_Creat.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_Creat)
        super(TextParagraph, self).__init__(intPtr)
    """
    <summary>
        Represents a paragraph of a text.
    </summary>
    """
    @property

    def FirstTextRange(self)->'TextRange':
        """
    <summary>
        First text range of text paragraph.
    </summary>
        """
        GetDllLibPpt().TextParagraph_get_FirstTextRange.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_FirstTextRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_get_FirstTextRange,self.Ptr)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret


    @property

    def TextRanges(self)->'TextRangeCollection':
        """
    <summary>
        Gets the collection of a text range.
            Readonly <see cref="T:Spire.Presentation.Collections.TextRangeCollection" />.
    </summary>
        """
        GetDllLibPpt().TextParagraph_get_TextRanges.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_TextRanges.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_get_TextRanges,self.Ptr)
        ret = None if intPtr==None else TextRangeCollection(intPtr)
        return ret


    @property

    def ParagraphProperties(self)->'TextParagraphProperties':
        """
    <summary>
        Gets the formatting of paragraph.
            Readonly <see cref="T:Spire.Presentation.TextParagraphProperties" />.
    </summary>
        """
        GetDllLibPpt().TextParagraph_get_ParagraphProperties.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_ParagraphProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextParagraph_get_ParagraphProperties,self.Ptr)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret


    @property

    def Text(self)->str:
        """
    <summary>
        Gets or sets the the plain text of a paragraph.
    </summary>
<value>
            The text.
            </value>
        """
        GetDllLibPpt().TextParagraph_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().TextParagraph_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextParagraph_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextParagraph_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextParagraph_set_Text,self.Ptr,valuePtr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextParagraph_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextParagraph_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextParagraph_Equals,self.Ptr, intPtrobj)
        return ret

