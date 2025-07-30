from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartEffectFormat (  PptObject, IChartEffectFormat) :
    """
    <summary>
        Represents chart format properties.
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
        GetDllLibPpt().ChartEffectFormat_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartEffectFormat_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Line,self.Ptr)
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
        GetDllLibPpt().ChartEffectFormat_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Effect,self.Ptr)
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
        GetDllLibPpt().ChartEffectFormat_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartEffectFormat_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartEffectFormat_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


