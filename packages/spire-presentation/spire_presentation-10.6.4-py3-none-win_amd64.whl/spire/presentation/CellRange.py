from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CellRange (SpireObject) :
    """
    <summary>
        Represents cell range for chart data
    </summary>
    """
    @property
    def Row(self)->int:
        """
    <summary>
        Gets the row.
    </summary>
        """
        GetDllLibPpt().CellRange_get_Row.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Row.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_get_Row,self.Ptr)
        return ret

    @property
    def Column(self)->int:
        """
    <summary>
        Gets the column.
    </summary>
        """
        GetDllLibPpt().CellRange_get_Column.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Column.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_get_Column,self.Ptr)
        return ret

    @property
    def NumberValue(self)->float:
        """
    <summary>
        Gets or set number value.
    </summary>
        """
        GetDllLibPpt().CellRange_get_NumberValue.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_NumberValue.restype=c_double
        ret = CallCFunction(GetDllLibPpt().CellRange_get_NumberValue,self.Ptr)
        return ret

    @NumberValue.setter
    def NumberValue(self, value:float):
        GetDllLibPpt().CellRange_set_NumberValue.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().CellRange_set_NumberValue,self.Ptr, value)

    @property

    def Text(self)->str:
        """
    <summary>
        Gets or set string value.
    </summary>
        """
        GetDllLibPpt().CellRange_get_Text.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Text.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().CellRange_get_Text,self.Ptr))
        return ret


    @Text.setter
    def Text(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().CellRange_set_Text.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().CellRange_set_Text,self.Ptr,valuePtr)

    @property

    def Value(self)->'SpireObject':
        """
    <summary>
        Gets or sets the value.
    </summary>
<value>
            The value.
            </value>
        """
        GetDllLibPpt().CellRange_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_Value.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRange_get_Value,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    @Value.setter
    def Value(self, value:'SpireObject'):
        GetDllLibPpt().CellRange_set_Value.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().CellRange_set_Value,self.Ptr, value.Ptr)

    @property

    def WorksheetName(self)->str:
        """
    <summary>
        Gets worksheet name.
    </summary>
        """
        GetDllLibPpt().CellRange_get_WorksheetName.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_WorksheetName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().CellRange_get_WorksheetName,self.Ptr))
        return ret


    @property
    def WorksheetIndex(self)->int:
        """
    <summary>
        Gets worksheet Index.
    </summary>
        """
        GetDllLibPpt().CellRange_get_WorksheetIndex.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_WorksheetIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_get_WorksheetIndex,self.Ptr)
        return ret

    @dispatch

    def Equals(self ,cellRange:'CellRange')->bool:
        """
    <summary>
        Indicates whether the specified <see cref="T:Spire.Presentation.Charts.CellRange" /> is equal to this instance.
    </summary>
    <param name="cellRange">The data cell.</param>
    <returns></returns>
        """
        intPtrcellRange:c_void_p = cellRange.Ptr

        GetDllLibPpt().CellRange_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRange_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CellRange_Equals,self.Ptr, intPtrcellRange)
        return ret

    @dispatch

    def Equals(self ,obj:SpireObject)->bool:
        """
    <summary>
        Indicates whether the specified <see cref="T:System.Object" /> is equal to this instance.
    </summary>
    <param name="obj">The <see cref="T:System.Object" /> to compare with this instance.</param>
    <returns>
  <c>true</c> if the specified <see cref="T:System.Object" /> is equal to this instance; otherwise, <c>false</c>.
            </returns>
<exception cref="T:System.NullReferenceException">
            The     <paramref name="obj" /> parameter is null.
              </exception>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CellRange_EqualsO.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRange_EqualsO.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CellRange_EqualsO,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
    <summary>
        Gets a hash code for this instance.
    </summary>
    <returns>
            A hash code for this instance, suitable for use in hashing algorithms and data structures like a hash table. 
            </returns>
        """
        GetDllLibPpt().CellRange_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRange_GetHashCode,self.Ptr)
        return ret

    @property

    def NumberFormat(self)->str:
        """
    <summary>
        set the number format of the chart data source(excel).
    </summary>
        """
        GetDllLibPpt().CellRange_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibPpt().CellRange_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().CellRange_get_NumberFormat,self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().CellRange_set_NumberFormat.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().CellRange_set_NumberFormat,self.Ptr,valuePtr)

