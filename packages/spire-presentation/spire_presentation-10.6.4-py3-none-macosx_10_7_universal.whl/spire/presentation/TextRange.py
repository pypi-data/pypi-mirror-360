from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class TextRange (  TextCharacterProperties) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().TextRange_Create.argtypes=[c_wchar_p]
        GetDllLibPpt().TextRange_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_Create,None)
        super(TextRange, self).__init__(intPtr)

    @dispatch
    def __init__(self,value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextRange_Create.argtypes=[c_char_p]
        GetDllLibPpt().TextRange_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_Create,valuePtr)
        super(TextRange, self).__init__(intPtr)
    """

    """
    @property

    def Format(self)->'DefaultTextRangeProperties':
        """
    <summary>
        Gets or sets text range's formatting.
            Readonly <see cref="!:DefaultTextRunProperties" />.
    </summary>
        """
        GetDllLibPpt().TextRange_get_Format.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Format.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_Format,self.Ptr)
        ret = None if intPtr==None else DefaultTextRangeProperties(intPtr)
        return ret

    @property

    def DisplayFormat(self)->'DefaultTextRangeProperties':
        """
    <summary>
        Gets or sets text range's Display formatting.
            Readonly <see cref="!:DefaultTextRunProperties" />.
    </summary>
        """
        GetDllLibPpt().TextRange_get_DisplayFormat.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_DisplayFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_DisplayFormat,self.Ptr)
        ret = None if intPtr==None else DefaultTextRangeProperties(intPtr)
        return ret

    @property

    def Paragraph(self)->'TextParagraph':
        """
    <summary>
        Gets paragraph of text range.
    </summary>
        """
        from spire.presentation.TextParagraph import TextParagraph
        GetDllLibPpt().TextRange_get_Paragraph.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Paragraph.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_Paragraph,self.Ptr)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret


    @property

    def Text(self)->str:
        """

        """
        GetDllLibPpt().TextRange_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextRange_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextRange_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextRange_set_Text,self.Ptr,valuePtr)

    @property

    def Field(self)->'Field':
        """

        """
        GetDllLibPpt().TextRange_get_Field.argtypes=[c_void_p]
        GetDllLibPpt().TextRange_get_Field.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRange_get_Field,self.Ptr)
        ret = None if intPtr==None else Field(intPtr)
        return ret



    def AddField(self ,fieldType:'FieldType'):
        """

        """
        intPtrfieldType:c_void_p = fieldType.Ptr

        GetDllLibPpt().TextRange_AddField.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().TextRange_AddField,self.Ptr, intPtrfieldType)

    def RemoveField(self):
        """

        """
        GetDllLibPpt().TextRange_RemoveField.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TextRange_RemoveField,self.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextRange_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextRange_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextRange_Equals,self.Ptr, intPtrobj)
        return ret

