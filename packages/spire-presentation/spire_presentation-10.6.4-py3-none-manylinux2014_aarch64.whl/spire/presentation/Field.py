from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Field (  PptObject) :
    """
    <summary>
        Represents a field.
    </summary>
    """
    @property

    def Type(self)->'FieldType':
        """
    <summary>
        Gets or sets type of field.
            Read/write <see cref="T:Spire.Presentation.FieldType" />.
    </summary>
        """
        GetDllLibPpt().Field_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().Field_get_Type.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Field_get_Type,self.Ptr)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @Type.setter
    def Type(self, value:'FieldType'):
        GetDllLibPpt().Field_set_Type.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Field_set_Type,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Field_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Field_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Field_Equals,self.Ptr, intPtrobj)
        return ret

