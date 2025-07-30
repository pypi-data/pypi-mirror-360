from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IChartEffectFormat (SpireObject) :
    """

    """
    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets fill style properties of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().IChartEffectFormat_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().IChartEffectFormat_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Line,self.Ptr)
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
        GetDllLibPpt().IChartEffectFormat_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Effect,self.Ptr)
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
        GetDllLibPpt().IChartEffectFormat_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
    <summary>
        Reference to Parent object. Read-only.
    </summary>
        """
        GetDllLibPpt().IChartEffectFormat_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IChartEffectFormat_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IChartEffectFormat_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().IChartEffectFormat_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IChartEffectFormat_Dispose,self.Ptr)

