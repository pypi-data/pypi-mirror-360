from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDataLabel (  PptObject) :
    """
    <summary>
        Represents a series labels.
    </summary>
    """
    @property

    def DataLabelSize(self)->'SizeF':
        """
    <summary>
        Size of DataLabel
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_DataLabelSize.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_DataLabelSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_DataLabelSize,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @DataLabelSize.setter
    def DataLabelSize(self, value:'SizeF'):
        GetDllLibPpt().ChartDataLabel_set_DataLabelSize.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_DataLabelSize,self.Ptr, value.Ptr)

    @property
    def IsDelete(self)->bool:
        """
    <summary>
        Gets or sets the label's delete flag.
            True means that data label was removed by user but preserved in file.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_IsDelete.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_IsDelete.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_IsDelete,self.Ptr)
        return ret

    @IsDelete.setter
    def IsDelete(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_IsDelete.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_IsDelete,self.Ptr, value)

    @property
    def ID(self)->int:
        """
    <summary>
        Specifies which data label are applied properties.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_ID.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_ID.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_ID,self.Ptr)
        return ret

    @ID.setter
    def ID(self, value:int):
        GetDllLibPpt().ChartDataLabel_set_ID.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_ID,self.Ptr, value)

    @property
    def HasDataSource(self)->bool:
        """
    <summary>
        Gets and sets a reference to the worksheet
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_HasDataSource.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_HasDataSource.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_HasDataSource,self.Ptr)
        return ret

    @HasDataSource.setter
    def HasDataSource(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_HasDataSource.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_HasDataSource,self.Ptr, value)

    @property

    def NumberFormat(self)->str:
        """
    <summary>
        Indicates the format string for the DataLabels object.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabel_get_NumberFormat,self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabel_set_NumberFormat.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_NumberFormat,self.Ptr,valuePtr)

    @property

    def TextFrame(self)->'ITextFrameProperties':
        """
    <summary>
        Gets a textframe of this data label.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
    <summary>
        Gets text properties.
            Readonly <see cref="T:Spire.Presentation.TextFrameProperties" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets fill style properties of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Line,self.Ptr)
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
        GetDllLibPpt().ChartDataLabel_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Effect,self.Ptr)
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
        GetDllLibPpt().ChartDataLabel_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def Position(self)->'ChartDataLabelPosition':
        """
    <summary>
        Indicates the position of the data lable.
            Read/write <see cref="T:Spire.Presentation.Charts.DataLabelPosition" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Position,self.Ptr)
        objwraped = ChartDataLabelPosition(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'ChartDataLabelPosition'):
        GetDllLibPpt().ChartDataLabel_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_Position,self.Ptr, value.value)

    @property
    def LegendKeyVisible(self)->bool:
        """
    <summary>
        Indicates whethere chart's data label legend key display behavior. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_LegendKeyVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_LegendKeyVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_LegendKeyVisible,self.Ptr)
        return ret

    @LegendKeyVisible.setter
    def LegendKeyVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_LegendKeyVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_LegendKeyVisible,self.Ptr, value)

    @property
    def CategoryNameVisible(self)->bool:
        """
    <summary>
        Indicates whethere chart's data label category name display behavior.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_CategoryNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_CategoryNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_CategoryNameVisible,self.Ptr)
        return ret

    @CategoryNameVisible.setter
    def CategoryNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_CategoryNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_CategoryNameVisible,self.Ptr, value)

    @property
    def LabelValueVisible(self)->bool:
        """
    <summary>
        Indicates whethere chart's data label percentage value display behavior. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_LabelValueVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_LabelValueVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_LabelValueVisible,self.Ptr)
        return ret

    @LabelValueVisible.setter
    def LabelValueVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_LabelValueVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_LabelValueVisible,self.Ptr, value)

    @property
    def PercentageVisible(self)->bool:
        """
    <summary>
        Indicates whethere chart's data label percentage value display behavior.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_PercentageVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_PercentageVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_PercentageVisible,self.Ptr)
        return ret

    @PercentageVisible.setter
    def PercentageVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_PercentageVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_PercentageVisible,self.Ptr, value)

    @property
    def SeriesNameVisible(self)->bool:
        """
    <summary>
        Indicates whethere the series name display behavior for the data labels on a chart. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_SeriesNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_SeriesNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_SeriesNameVisible,self.Ptr)
        return ret

    @SeriesNameVisible.setter
    def SeriesNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_SeriesNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_SeriesNameVisible,self.Ptr, value)

    @property
    def BubbleSizeVisible(self)->bool:
        """
    <summary>
        Indicates whethere chart's data label bubble size value will display. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_BubbleSizeVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_BubbleSizeVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_BubbleSizeVisible,self.Ptr)
        return ret

    @BubbleSizeVisible.setter
    def BubbleSizeVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_BubbleSizeVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_BubbleSizeVisible,self.Ptr, value)

    @property

    def Separator(self)->str:
        """
    <summary>
        Gets or sets the separator used for the data labels on a chart.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_Separator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Separator.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabel_get_Separator,self.Ptr))
        return ret


    @Separator.setter
    def Separator(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabel_set_Separator.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_Separator,self.Ptr,valuePtr)

    @property
    def X(self)->float:
        """
    <summary>
        Specifies the x location(left) of the dataLabel as a fraction of the width of the chart.
            The position is relative to the default position.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_X.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_X.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_X,self.Ptr)
        return ret

    @X.setter
    def X(self, value:float):
        GetDllLibPpt().ChartDataLabel_set_X.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_X,self.Ptr, value)

    @property
    def Y(self)->float:
        """
    <summary>
        Specifies the y location(top) of the dataLabel as a fraction of the height of the chart.
            The position is relative to the default position.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_Y.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_Y.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_Y,self.Ptr)
        return ret

    @Y.setter
    def Y(self, value:float):
        GetDllLibPpt().ChartDataLabel_set_Y.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_Y,self.Ptr, value)

    @property
    def RotationAngle(self)->float:
        """
    <summary>
        Gets or sets rotation angle of chart's data label.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_RotationAngle.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_RotationAngle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_RotationAngle,self.Ptr)
        return ret

    @RotationAngle.setter
    def RotationAngle(self, value:float):
        GetDllLibPpt().ChartDataLabel_set_RotationAngle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_RotationAngle,self.Ptr, value)

    @property

    def DataLabelShapeType(self)->'DataLabelShapeType':
        """
    <summary>
        Gets or sets shape type of data label.
            Read/write <see cref="P:Spire.Presentation.Charts.ChartDataLabel.DataLabelShapeType" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_DataLabelShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_DataLabelShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_DataLabelShapeType,self.Ptr)
        objwraped = DataLabelShapeType(ret)
        return objwraped

    @DataLabelShapeType.setter
    def DataLabelShapeType(self, value:'DataLabelShapeType'):
        GetDllLibPpt().ChartDataLabel_set_DataLabelShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_DataLabelShapeType,self.Ptr, value.value)

    @property
    def ShowDataLabelsRange(self)->bool:
        """
    <summary>
        if show data labels range.
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_ShowDataLabelsRange.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_ShowDataLabelsRange.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_ShowDataLabelsRange,self.Ptr)
        return ret

    @ShowDataLabelsRange.setter
    def ShowDataLabelsRange(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_ShowDataLabelsRange.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_ShowDataLabelsRange,self.Ptr, value)

    @property
    def UseValuePlaceholder(self)->bool:
        """
    <summary>
        If use ValuePlaceholder
    </summary>
        """
        GetDllLibPpt().ChartDataLabel_get_UseValuePlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabel_get_UseValuePlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabel_get_UseValuePlaceholder,self.Ptr)
        return ret

    @UseValuePlaceholder.setter
    def UseValuePlaceholder(self, value:bool):
        GetDllLibPpt().ChartDataLabel_set_UseValuePlaceholder.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabel_set_UseValuePlaceholder,self.Ptr, value)

    @staticmethod

    def ValuePlaceholder()->str:
        """
    <summary>
        Use the ValuePlaceholder to represent chart value
    </summary>
        """
        #GetDllLibPpt().ChartDataLabel_ValuePlaceholder.argtypes=[]
        GetDllLibPpt().ChartDataLabel_ValuePlaceholder.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabel_ValuePlaceholder))
        return ret


