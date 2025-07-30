from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ChartDataPoint (  PptObject) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().ChartDataPoint_Creat.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_Creat)
        super(ChartDataPoint, self).__init__(intPtr)

    @dispatch
    def __init__(self,param):
        if isinstance(param, (int,float)):
            super(ChartDataPoint, self).__init__(param)
        else:
            GetDllLibPpt().ChartDataPoint_Creat.argtypes = [c_void_p]
            GetDllLibPpt().ChartDataPoint_Creat.restype = c_void_p
            intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_Creat,param.Ptr)
            super(ChartDataPoint, self).__init__(intPtr)
    
    """
    <summary>
        Represents a data point on the chart.
    </summary>
    """
    @property
    def Index(self)->int:
        """
    <summary>
        This index of collection.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_Index.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Index,self.Ptr)
        return ret

    @Index.setter
    def Index(self, value:int):
        GetDllLibPpt().ChartDataPoint_set_Index.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_Index,self.Ptr, value)

    @property
    def IsBubble3D(self)->bool:
        """
    <summary>
        Specifies that the bubbles have a 3-D effect applied to them.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_IsBubble3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_IsBubble3D.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_IsBubble3D,self.Ptr)
        return ret

    @IsBubble3D.setter
    def IsBubble3D(self, value:bool):
        GetDllLibPpt().ChartDataPoint_set_IsBubble3D.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_IsBubble3D,self.Ptr, value)

    @property
    def Distance(self)->int:
        """
    <summary>
        Specifies the distance from the center of the pie.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Distance.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:int):
        GetDllLibPpt().ChartDataPoint_set_Distance.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_Distance,self.Ptr, value)

    @property
    def InvertIfNegative(self)->bool:
        """
    <summary>
        Indicates whether invert its colors if the value is negative.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_InvertIfNegative.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_InvertIfNegative.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_InvertIfNegative,self.Ptr)
        return ret

    @InvertIfNegative.setter
    def InvertIfNegative(self, value:bool):
        GetDllLibPpt().ChartDataPoint_set_InvertIfNegative.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_InvertIfNegative,self.Ptr, value)

    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets fill style properties of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
    <summary>
        Gets effects used for a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.EffectDag" />.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
    <summary>
        Gets 3D format of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FormatThreeD" />.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def MarkerFill(self)->'ChartEffectFormat':
        """
    <summary>
        Represents the formatting properties for marker.
            A chart with Bubble type or Bubble3D type does not support this property.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_MarkerFill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_MarkerFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataPoint_get_MarkerFill,self.Ptr)
        ret = None if intPtr==None else ChartEffectFormat(intPtr)
        return ret


    @property
    def MarkerSize(self)->int:
        """
    <summary>
        Represents the marker size in a line chart, scatter chart, or radar chart.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_MarkerSize.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_MarkerSize.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_MarkerSize,self.Ptr)
        return ret

    @MarkerSize.setter
    def MarkerSize(self, value:int):
        GetDllLibPpt().ChartDataPoint_set_MarkerSize.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_MarkerSize,self.Ptr, value)

    @property

    def MarkerStyle(self)->'ChartMarkerType':
        """
    <summary>
        Represents the marker style in a line chart, scatter chart, or radar chart.
    </summary>
        """
        GetDllLibPpt().ChartDataPoint_get_MarkerStyle.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_MarkerStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_MarkerStyle,self.Ptr)
        objwraped = ChartMarkerType(ret)
        return objwraped

    @MarkerStyle.setter
    def MarkerStyle(self, value:'ChartMarkerType'):
        GetDllLibPpt().ChartDataPoint_set_MarkerStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_MarkerStyle,self.Ptr, value.value)

    @property
    def SetAsTotal(self)->bool:
        """
    <summary>
         True if the data point is considered as Subtotals or Totals. otherwise False.
    </summary>
<remarks>Applies only to Waterfall charts.</remarks>
        """
        GetDllLibPpt().ChartDataPoint_get_SetAsTotal.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataPoint_get_SetAsTotal.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataPoint_get_SetAsTotal,self.Ptr)
        return ret

    @SetAsTotal.setter
    def SetAsTotal(self, value:bool):
        GetDllLibPpt().ChartDataPoint_set_SetAsTotal.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataPoint_set_SetAsTotal,self.Ptr, value)

