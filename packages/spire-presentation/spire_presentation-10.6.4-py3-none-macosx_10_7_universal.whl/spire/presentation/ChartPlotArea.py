from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartPlotArea (SpireObject) :
    """
    <summary>
        Represents rectangle where chart should be plotted.
    </summary>
    """
    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets fill style properties of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartPlotArea_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartPlotArea_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Line,self.Ptr)
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
        GetDllLibPpt().ChartPlotArea_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Effect,self.Ptr)
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
        GetDllLibPpt().ChartPlotArea_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property
    def Left(self)->float:
        """
    <summary>
        Gets or sets the upper left corner of plot area bounding box in range from 0 to 1 of chart area.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartPlotArea_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
         Gets or sets top corner of plot area bounding box in range from 0 to 1 of chart area.
             Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartPlotArea_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
    <summary>
        Get or sets the Width of plot area.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartPlotArea_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Get or sets the Height of plot area.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartPlotArea_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ChartPlotArea_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartPlotArea_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ChartPlotArea_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartPlotArea_set_Height,self.Ptr, value)

