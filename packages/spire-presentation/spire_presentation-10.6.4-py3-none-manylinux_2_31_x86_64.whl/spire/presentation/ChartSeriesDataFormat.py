from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartSeriesDataFormat (  PptObject) :
    """
    <summary>
        Represents a chart series.
    </summary>
    """
    @property

    def MarkerFill(self)->'IChartEffectFormat':
        """
    <summary>
        Gets or sets the marker fill
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_MarkerFill.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_MarkerFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_MarkerFill,self.Ptr)
        ret = None if intPtr==None else IChartEffectFormat(intPtr)
        return ret


    @property
    def Distance(self)->int:
        """
    <summary>
         The distance from the center of the pie chart is expressed as a percentage of the pie.
     </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Distance.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:int):
        GetDllLibPpt().ChartSeriesDataFormat_set_Distance.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_Distance,self.Ptr, value)

    @property

    def IsSmooth(self)->'TriState':
        """
    <summary>
        Represents curve smoothing. 
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_IsSmooth.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_IsSmooth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_IsSmooth,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @IsSmooth.setter
    def IsSmooth(self, value:'TriState'):
        GetDllLibPpt().ChartSeriesDataFormat_set_IsSmooth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_IsSmooth,self.Ptr, value.value)

    @property
    def MarkerSize(self)->int:
        """
    <summary>
        Represents the marker size in a line chart, scatter chart, or radar chart.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_MarkerSize.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_MarkerSize.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_MarkerSize,self.Ptr)
        return ret

    @MarkerSize.setter
    def MarkerSize(self, value:int):
        GetDllLibPpt().ChartSeriesDataFormat_set_MarkerSize.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_MarkerSize,self.Ptr, value)

    @property

    def MarkerStyle(self)->'ChartMarkerType':
        """
    <summary>
        Represents the marker style in a line chart, scatter chart, or radar chart.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_MarkerStyle.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_MarkerStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_MarkerStyle,self.Ptr)
        objwraped = ChartMarkerType(ret)
        return objwraped

    @MarkerStyle.setter
    def MarkerStyle(self, value:'ChartMarkerType'):
        GetDllLibPpt().ChartSeriesDataFormat_set_MarkerStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_MarkerStyle,self.Ptr, value.value)

    @property

    def NamedRange(self)->'CellRanges':
        """
    <summary>
        Gets collection of cells with series names.
            Read-only <see cref="T:Spire.Presentation.Collections.CellRanges" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_NamedRange.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_NamedRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_NamedRange,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @property

    def XValues(self)->'CellRanges':
        """
    <summary>
        Gets collection of cells with XValues.
            Read-only <see cref="T:Spire.Presentation.Collections.CellRanges" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_XValues.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_XValues.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_XValues,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @XValues.setter
    def XValues(self, value:'CellRanges'):
        GetDllLibPpt().ChartSeriesDataFormat_set_XValues.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_XValues,self.Ptr, value.Ptr)

    @property

    def ErrorBarsXFormat(self)->'IErrorBarsFormat':
        """
    <summary>
        Gets X-ErrorBar of a series.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ErrorBarsXFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ErrorBarsXFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ErrorBarsXFormat,self.Ptr)
        ret = None if intPtr==None else IErrorBarsFormat(intPtr)
        return ret


    @property

    def ErrorBarsYFormat(self)->'IErrorBarsFormat':
        """
    <summary>
        Gets Y-ErrorBar of a series.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ErrorBarsYFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ErrorBarsYFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ErrorBarsYFormat,self.Ptr)
        ret = None if intPtr==None else IErrorBarsFormat(intPtr)
        return ret


    @property

    def YValues(self)->'CellRanges':
        """
    <summary>
        Gets collection of cells with YValues.
            Read-only <see cref="T:Spire.Presentation.Collections.CellRanges" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_YValues.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_YValues.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_YValues,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @YValues.setter
    def YValues(self, value:'CellRanges'):
        GetDllLibPpt().ChartSeriesDataFormat_set_YValues.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_YValues,self.Ptr, value.Ptr)

    @property

    def Bubbles(self)->'CellRanges':
        """
    <summary>
        Gets collection of cells with bubbleSize.
            Read-only <see cref="T:Spire.Presentation.Collections.CellRanges" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_Bubbles.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Bubbles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Bubbles,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @Bubbles.setter
    def Bubbles(self, value:'CellRanges'):
        GetDllLibPpt().ChartSeriesDataFormat_set_Bubbles.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_Bubbles,self.Ptr, value.Ptr)

    @property

    def Values(self)->'CellRanges':
        """
    <summary>
        Gets collection of cells with values.
            Read-only <see cref="T:Spire.Presentation.Collections.CellRanges" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_Values.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Values.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Values,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @Values.setter
    def Values(self, value:'CellRanges'):
        GetDllLibPpt().ChartSeriesDataFormat_set_Values.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_Values,self.Ptr, value.Ptr)

    @property

    def Type(self)->'ChartType':
        """
    <summary>
        Get chart type.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Type,self.Ptr)
        objwraped = ChartType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'ChartType'):
        GetDllLibPpt().ChartSeriesDataFormat_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_Type,self.Ptr, value.value)

    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets fill style properties of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Line,self.Ptr)
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
        GetDllLibPpt().ChartSeriesDataFormat_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Effect,self.Ptr)
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
        GetDllLibPpt().ChartSeriesDataFormat_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property
    def Index(self)->int:
        """
    <summary>
        Gets the index of a series.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_Index.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_Index,self.Ptr)
        return ret

    @Index.setter
    def Index(self, value:int):
        GetDllLibPpt().ChartSeriesDataFormat_set_Index.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_Index,self.Ptr, value)

    @property

    def DataLabels(self)->'ChartDataLabelCollection':
        """
    <summary>
        Gets the Labels of a series.
            Read-only <see cref="T:Spire.Presentation.Collections.ChartDataLabelCollection" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_DataLabels.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_DataLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_DataLabels,self.Ptr)
        ret = None if intPtr==None else ChartDataLabelCollection(intPtr)
        return ret


    @property

    def DataLabelRanges(self)->'CellRanges':
        """
    <summary>
        Gets or set the Labels ranges of a series.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_DataLabelRanges.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_DataLabelRanges.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_DataLabelRanges,self.Ptr)
        ret = None if intPtr==None else CellRanges(intPtr)
        return ret


    @DataLabelRanges.setter
    def DataLabelRanges(self, value:'CellRanges'):
        GetDllLibPpt().ChartSeriesDataFormat_set_DataLabelRanges.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_DataLabelRanges,self.Ptr, value.Ptr)

    @property
    def TrendLines(self)->List['ITrendlines']:
       
        GetDllLibPpt().ChartSeriesDataFormat_get_TrendLines.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_TrendLines.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_TrendLines,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, ITrendlines)
        return ret

    def AddTrendLine(self ,type:'TrendlinesType')->'ITrendlines':
        """

        """
        enumtype:c_int = type.value

        GetDllLibPpt().ChartSeriesDataFormat_AddTrendLine.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartSeriesDataFormat_AddTrendLine.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_AddTrendLine,self.Ptr, enumtype)
        ret = None if intPtr==None else ITrendlines(intPtr)
        return ret


    @property
    def UseSecondAxis(self)->bool:
        """
    <summary>
        Indicates whether this series use second value axis or not.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_UseSecondAxis.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_UseSecondAxis.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_UseSecondAxis,self.Ptr)
        return ret

    @UseSecondAxis.setter
    def UseSecondAxis(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_UseSecondAxis.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_UseSecondAxis,self.Ptr, value)

    @property

    def DataPoints(self)->'ChartDataPointCollection':
        """
    <summary>
        Gets the Points Collection of a series.
            Read-only <see cref="T:Spire.Presentation.Collections.ChartDataPointCollection" />.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_DataPoints.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_DataPoints.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_DataPoints,self.Ptr)
        ret = None if intPtr==None else ChartDataPointCollection(intPtr)
        return ret


    @property
    def IsVaryColor(self)->bool:
        """
    <summary>
        Indicates that color of point is varied. 
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_IsVaryColor.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_IsVaryColor.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_IsVaryColor,self.Ptr)
        return ret

    @IsVaryColor.setter
    def IsVaryColor(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_IsVaryColor.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_IsVaryColor,self.Ptr, value)

    @property
    def HasSeriesLines(self)->bool:
        """
    <summary>
        Indicates that chart has series lines.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_HasSeriesLines.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_HasSeriesLines.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_HasSeriesLines,self.Ptr)
        return ret

    @HasSeriesLines.setter
    def HasSeriesLines(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_HasSeriesLines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_HasSeriesLines,self.Ptr, value)

    @property

    def FirstSliceAngleInPieChart(self)->'UInt16':
        """
    <summary>
         Gets or sets the angle of the pie-chart in degrees 
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_FirstSliceAngleInPieChart.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_FirstSliceAngleInPieChart.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_FirstSliceAngleInPieChart,self.Ptr)
        ret = None if intPtr==None else UInt16(intPtr)
        return ret


    @FirstSliceAngleInPieChart.setter
    def FirstSliceAngleInPieChart(self, value:'UInt16'):
        GetDllLibPpt().ChartSeriesDataFormat_set_FirstSliceAngleInPieChart.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_FirstSliceAngleInPieChart,self.Ptr, value.Ptr)

    @property
    def DoughnutHoleSize(self)->int:
        """
    <summary>
        Returns or sets the size of the hole in a doughnut chart. 
            The hole size is expressed as percentage of the of chart size , between 10 and 90 percent.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_DoughnutHoleSize.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_DoughnutHoleSize.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_DoughnutHoleSize,self.Ptr)
        return ret

    @DoughnutHoleSize.setter
    def DoughnutHoleSize(self, value:int):
        GetDllLibPpt().ChartSeriesDataFormat_set_DoughnutHoleSize.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_DoughnutHoleSize,self.Ptr, value)

    @property
    def InvertIfNegative(self)->bool:
        """
    <summary>
        Specifies invert colors if the value is negative
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_InvertIfNegative.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_InvertIfNegative.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_InvertIfNegative,self.Ptr)
        return ret

    @InvertIfNegative.setter
    def InvertIfNegative(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_InvertIfNegative.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_InvertIfNegative,self.Ptr, value)

    @property
    def IsHidden(self)->bool:
        """
    <summary>
        Specifies whether the series is hidden.
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_IsHidden,self.Ptr, value)

    @property
    def ShowConnectorLines(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display 
            Connector Lines between data points
    </summary>
<remarks>Applies only to Waterfall Charts</remarks>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowConnectorLines.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowConnectorLines.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ShowConnectorLines,self.Ptr)
        return ret

    @ShowConnectorLines.setter
    def ShowConnectorLines(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_ShowConnectorLines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_ShowConnectorLines,self.Ptr, value)

    @property
    def ShowInnerPoints(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Inner Points in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowInnerPoints.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowInnerPoints.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ShowInnerPoints,self.Ptr)
        return ret

    @ShowInnerPoints.setter
    def ShowInnerPoints(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_ShowInnerPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_ShowInnerPoints,self.Ptr, value)

    @property
    def ShowOutlierPoints(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Outlier Points in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowOutlierPoints.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowOutlierPoints.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ShowOutlierPoints,self.Ptr)
        return ret

    @ShowOutlierPoints.setter
    def ShowOutlierPoints(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_ShowOutlierPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_ShowOutlierPoints,self.Ptr, value)

    @property
    def ShowMeanMarkers(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Mean Marker in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowMeanMarkers.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowMeanMarkers.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ShowMeanMarkers,self.Ptr)
        return ret

    @ShowMeanMarkers.setter
    def ShowMeanMarkers(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_ShowMeanMarkers.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_ShowMeanMarkers,self.Ptr, value)

    @property
    def ShowMeanLine(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Mean Line in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowMeanLine.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ShowMeanLine.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ShowMeanLine,self.Ptr)
        return ret

    @ShowMeanLine.setter
    def ShowMeanLine(self, value:bool):
        GetDllLibPpt().ChartSeriesDataFormat_set_ShowMeanLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_ShowMeanLine,self.Ptr, value)

    @property

    def QuartileCalculationType(self)->'QuartileCalculation':
        """
    <summary>
         Gets / Sets whether the Quartile calculation is Exclusive or Inclusive
    </summary>
<remarks>Applies only to Box and Whisker Charts</remarks>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_QuartileCalculationType.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_QuartileCalculationType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_QuartileCalculationType,self.Ptr)
        objwraped = QuartileCalculation(ret)
        return objwraped

    @QuartileCalculationType.setter
    def QuartileCalculationType(self, value:'QuartileCalculation'):
        GetDllLibPpt().ChartSeriesDataFormat_set_QuartileCalculationType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_QuartileCalculationType,self.Ptr, value.value)

    @property

    def TreeMapLabelOption(self)->'TreeMapLabelOption':
        """
    <summary>
        Gets / Sets the Display label position in Tree map chart
    </summary>
<remarks>By Default the Label is overlapped</remarks>
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_TreeMapLabelOption.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_TreeMapLabelOption.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_TreeMapLabelOption,self.Ptr)
        objwraped = TreeMapLabelOption(ret)
        return objwraped
    

    @TreeMapLabelOption.setter
    def TreeMapLabelOption(self, value:'TreeMapLabelOption'):
        GetDllLibPpt().ChartSeriesDataFormat_set_TreeMapLabelOption.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_TreeMapLabelOption,self.Ptr, value.value)

    @property

    def ProjectionType(self)->'ProjectionType':
        """
        """
        GetDllLibPpt().ChartSeriesDataFormat_get_ProjectionType.argtypes=[c_void_p]
        GetDllLibPpt().ChartSeriesDataFormat_get_ProjectionType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_get_ProjectionType,self.Ptr)
        objwraped = ProjectionType(ret)
        return objwraped
    
    @ProjectionType.setter
    def ProjectionType(self, type:'ProjectionType'):
        enumtype:c_int = type.value
        GetDllLibPpt().ChartSeriesDataFormat_set_ProjectionType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartSeriesDataFormat_set_ProjectionType,self.Ptr, enumtype)

