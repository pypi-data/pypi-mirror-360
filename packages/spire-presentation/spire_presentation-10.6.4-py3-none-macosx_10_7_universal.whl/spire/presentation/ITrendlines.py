from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITrendlines (SpireObject) :
    """

    """
    @property
    def backward(self)->float:
        """
    <summary>
        Gets or sets the Backward.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_backward.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_backward.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_backward,self.Ptr)
        return ret

    @backward.setter
    def backward(self, value:float):
        GetDllLibPpt().ITrendlines_set_backward.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlines_set_backward,self.Ptr, value)

    @property
    def forward(self)->float:
        """
    <summary>
        Gets or sets the Forward.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_forward.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_forward.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_forward,self.Ptr)
        return ret

    @forward.setter
    def forward(self, value:float):
        GetDllLibPpt().ITrendlines_set_forward.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlines_set_forward,self.Ptr, value)

    @property
    def intercept(self)->float:
        """
    <summary>
        Gets or sets the Intercept.Supported only exp,line or poly type. 
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_intercept.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_intercept.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_intercept,self.Ptr)
        return ret

    @intercept.setter
    def intercept(self, value:float):
        GetDllLibPpt().ITrendlines_set_intercept.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlines_set_intercept,self.Ptr, value)

    @property
    def displayEquation(self)->bool:
        """
    <summary>
        Gets or sets the DisplayEquation. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_displayEquation.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_displayEquation.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_displayEquation,self.Ptr)
        return ret

    @displayEquation.setter
    def displayEquation(self, value:bool):
        GetDllLibPpt().ITrendlines_set_displayEquation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITrendlines_set_displayEquation,self.Ptr, value)

    @property
    def displayRSquaredValue(self)->bool:
        """
    <summary>
        Gets or sets the DisplayRSquaredValue. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_displayRSquaredValue.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_displayRSquaredValue.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_displayRSquaredValue,self.Ptr)
        return ret

    @displayRSquaredValue.setter
    def displayRSquaredValue(self, value:bool):
        GetDllLibPpt().ITrendlines_set_displayRSquaredValue.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITrendlines_set_displayRSquaredValue,self.Ptr, value)

    @property
    def polynomialTrendlineOrder(self)->int:
        """
    <summary>
        Gets or sets the Order only for Polynomial Trendline. between 2 and 6. 
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_polynomialTrendlineOrder.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_polynomialTrendlineOrder.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_polynomialTrendlineOrder,self.Ptr)
        return ret

    @polynomialTrendlineOrder.setter
    def polynomialTrendlineOrder(self, value:int):
        GetDllLibPpt().ITrendlines_set_polynomialTrendlineOrder.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITrendlines_set_polynomialTrendlineOrder,self.Ptr, value)

    @property
    def period(self)->int:
        """
    <summary>
        Gets or sets the Period only for Moving Average Trendline. between 2 and 255. 
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_period.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_period.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_period,self.Ptr)
        return ret

    @period.setter
    def period(self, value:int):
        GetDllLibPpt().ITrendlines_set_period.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITrendlines_set_period,self.Ptr, value)

    @property

    def type(self)->'TrendlinesType':
        """
    <summary>
        Gets or sets the TrendlinesType. 
            Read/write <see cref="T:Spire.Presentation.Charts.TrendlinesType" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_type.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITrendlines_get_type,self.Ptr)
        objwraped = TrendlinesType(ret)
        return objwraped

    @type.setter
    def type(self, value:'TrendlinesType'):
        GetDllLibPpt().ITrendlines_set_type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITrendlines_set_type,self.Ptr, value.value)

    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the TrendlinesName. 
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ITrendlines_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITrendlines_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITrendlines_set_Name,self.Ptr,valuePtr)

    @property

    def Line(self)->'TextLineFormat':
        """
    <summary>
        Gets or sets the TrendlinesLine. 
            Read <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlines_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
    <summary>
        Gets or sets the Trendlines Effect. 
            Read <see cref="T:Spire.Presentation.Drawing.EffectDag" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlines_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def TrendLineLabel(self)->'ITrendlineLabel':
        """
    <summary>
        Gets the Trendlines DataLabel. 
            Read <see cref="T:Spire.Presentation.Charts.ITrendlineLabel" />.
    </summary>
        """
        GetDllLibPpt().ITrendlines_get_TrendLineLabel.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlines_get_TrendLineLabel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlines_get_TrendLineLabel,self.Ptr)
        ret = None if intPtr==None else ITrendlineLabel(intPtr)
        return ret


