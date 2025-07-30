from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartLegend (SpireObject) :
    """
    <summary>
        Represents chart's legend properties.
    </summary>
    """
    @property
    def Width(self)->float:
        """
    <summary>
        Gets or sets the width of a legend.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ChartLegend_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Gets or sets the height of a legend.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ChartLegend_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Height,self.Ptr, value)

    @property
    def Left(self)->float:
        """
    <summary>
        Gets or sets the x coordinate of a legend.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().ChartLegend_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
        Gets or sets the y coordinate of a legend.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().ChartLegend_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Top,self.Ptr, value)

    @property
    def IsOverlay(self)->bool:
        """
    <summary>
        Indicates whether other chart elements allowed to overlap legend.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_IsOverlay.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_IsOverlay.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_IsOverlay,self.Ptr)
        return ret

    @IsOverlay.setter
    def IsOverlay(self, value:bool):
        GetDllLibPpt().ChartLegend_set_IsOverlay.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartLegend_set_IsOverlay,self.Ptr, value)

    @property

    def Position(self)->'ChartLegendPositionType':
        """
    <summary>
        Gets or sets the position of the legend on a chart.
            Read/write <see cref="T:Spire.Presentation.Charts.ChartLegendPositionType" />.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartLegend_get_Position,self.Ptr)
        objwraped = ChartLegendPositionType(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'ChartLegendPositionType'):
        GetDllLibPpt().ChartLegend_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartLegend_set_Position,self.Ptr, value.value)

    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets fill style properties of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Line,self.Ptr)
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
        GetDllLibPpt().ChartLegend_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Effect,self.Ptr)
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
        GetDllLibPpt().ChartLegend_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
    <summary>
        Represent text properties of Legend
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret



    def setEntrys(self ,range:'CellRanges'):
        """
    <summary>
        set Legend Entry
    </summary>
        """
        intPtrrange:c_void_p = range.Ptr

        GetDllLibPpt().ChartLegend_setEntrys.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartLegend_setEntrys,self.Ptr, intPtrrange)


    def DeleteEntry(self ,index:int):
        """
    <summary>
        Delete legend entry by index
    </summary>
    <param name="index">The legend entry index must be between 0 and LegendCount - 1 + TrendLinesCount</param>
        """
        
        GetDllLibPpt().ChartLegend_DeleteEntry.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ChartLegend_DeleteEntry,self.Ptr, index)

    @property

    def EntryTextProperties(self)->List['TextCharacterProperties']:
        """
    <summary>
        Represent text properties of Legend Entry
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_EntryTextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_EntryTextProperties.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ChartLegend_get_EntryTextProperties,self.Ptr)
        ret = GetObjVectorFromArray (intPtrArray, TextCharacterProperties)
        return ret


    @property

    def LegendEntrys(self)->'LegendEntryCollection':
        """
    <summary>
        Get legend entry collection.
    </summary>
        """
        GetDllLibPpt().ChartLegend_get_LegendEntrys.argtypes=[c_void_p]
        GetDllLibPpt().ChartLegend_get_LegendEntrys.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartLegend_get_LegendEntrys,self.Ptr)
        ret = None if intPtr==None else LegendEntryCollection(intPtr)
        return ret


