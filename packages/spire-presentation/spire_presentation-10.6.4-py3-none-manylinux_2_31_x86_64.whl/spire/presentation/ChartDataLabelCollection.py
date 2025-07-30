from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDataLabelCollection (  SpireObject ) :
    """
    <summary>
        Represents a series labels.
    </summary>
    """
    @property

    def NumberFormat(self)->str:
        """
    <summary>
        Represents the format string for the DataLabels object.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_NumberFormat.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_NumberFormat.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_NumberFormat,self.Ptr))
        return ret


    @NumberFormat.setter
    def NumberFormat(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabelCollection_set_NumberFormat.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_NumberFormat,self.Ptr,valuePtr)

    @property
    def HasDataSource(self)->bool:
        """
    <summary>
        Gets and sets a reference to the worksheet
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_HasDataSource.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_HasDataSource.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_HasDataSource,self.Ptr)
        return ret

    @HasDataSource.setter
    def HasDataSource(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_HasDataSource.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_HasDataSource,self.Ptr, value)

    @property
    def IsDelete(self)->bool:
        """
    <summary>
        Gets or sets delete flag.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_IsDelete.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_IsDelete.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_IsDelete,self.Ptr)
        return ret

    @IsDelete.setter
    def IsDelete(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_IsDelete.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_IsDelete,self.Ptr, value)

    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
    <summary>
        Gets a text properties of this data labels
            Readonly <see cref="T:Spire.Presentation.TextFrameProperties" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_TextProperties,self.Ptr)
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
        GetDllLibPpt().ChartDataLabelCollection_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Line,self.Ptr)
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
        GetDllLibPpt().ChartDataLabelCollection_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Effect,self.Ptr)
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
        GetDllLibPpt().ChartDataLabelCollection_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def Position(self)->'ChartDataLabelPosition':
        """
    <summary>
        Represents the position of the data lable.
            Read/write <see cref="T:Spire.Presentation.Charts.DataLabelPosition" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Position,self.Ptr)
        objwraped = ChartDataLabelPosition(ret)
        return objwraped

    @Position.setter
    def Position(self, value:'ChartDataLabelPosition'):
        GetDllLibPpt().ChartDataLabelCollection_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_Position,self.Ptr, value.value)

    @property
    def LegendKeyVisible(self)->bool:
        """
    <summary>
        Indicates chart's data label legend key display behavior. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_LegendKeyVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LegendKeyVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LegendKeyVisible,self.Ptr)
        return ret

    @LegendKeyVisible.setter
    def LegendKeyVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_LegendKeyVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_LegendKeyVisible,self.Ptr, value)

    @property
    def LeaderLinesVisible(self)->bool:
        """
    <summary>
        Indicates chart's data label leader line display behavior. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLinesVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLinesVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LeaderLinesVisible,self.Ptr)
        return ret

    @LeaderLinesVisible.setter
    def LeaderLinesVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_LeaderLinesVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_LeaderLinesVisible,self.Ptr, value)

    @property
    def CategoryNameVisible(self)->bool:
        """
    <summary>
        Indicates chart's data label category name display behavior.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_CategoryNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_CategoryNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_CategoryNameVisible,self.Ptr)
        return ret

    @CategoryNameVisible.setter
    def CategoryNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_CategoryNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_CategoryNameVisible,self.Ptr, value)

    @property
    def LabelValueVisible(self)->bool:
        """
    <summary>
        Indicates chart's data label value display behavior.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_LabelValueVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LabelValueVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LabelValueVisible,self.Ptr)
        return ret

    @LabelValueVisible.setter
    def LabelValueVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_LabelValueVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_LabelValueVisible,self.Ptr, value)

    @property
    def PercentValueVisible(self)->bool:
        """
    <summary>
        Indicates chart's data label percentage value display behavior.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_PercentValueVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_PercentValueVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_PercentValueVisible,self.Ptr)
        return ret

    @PercentValueVisible.setter
    def PercentValueVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_PercentValueVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_PercentValueVisible,self.Ptr, value)

    @property
    def SeriesNameVisible(self)->bool:
        """
    <summary>
        Gets or sets a Boolean to indicate the series name display behavior for the data labels on a chart. 
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_SeriesNameVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_SeriesNameVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_SeriesNameVisible,self.Ptr)
        return ret

    @SeriesNameVisible.setter
    def SeriesNameVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_SeriesNameVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_SeriesNameVisible,self.Ptr, value)

    @property
    def BubbleSizeVisible(self)->bool:
        """
    <summary>
        Indicates chart's data label bubble size value display behavior.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_BubbleSizeVisible.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_BubbleSizeVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_BubbleSizeVisible,self.Ptr)
        return ret

    @BubbleSizeVisible.setter
    def BubbleSizeVisible(self, value:bool):
        GetDllLibPpt().ChartDataLabelCollection_set_BubbleSizeVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_BubbleSizeVisible,self.Ptr, value)

    @property

    def Separator(self)->str:
        """
    <summary>
        Sets or returns a Variant representing the separator used for the data labels on a chart.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Separator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Separator.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Separator,self.Ptr))
        return ret


    @Separator.setter
    def Separator(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ChartDataLabelCollection_set_Separator.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_Separator,self.Ptr,valuePtr)

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Count,self.Ptr)
        return ret

    @property

    def DataLabelShapeType(self)->'DataLabelShapeType':
        """
    <summary>
        Gets or sets shape type of data labels.
            Read/write <see cref="P:Spire.Presentation.Collections.ChartDataLabelCollection.DataLabelShapeType" />.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_get_DataLabelShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_DataLabelShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_DataLabelShapeType,self.Ptr)
        objwraped = DataLabelShapeType(ret)
        return objwraped

    @DataLabelShapeType.setter
    def DataLabelShapeType(self, value:'DataLabelShapeType'):
        GetDllLibPpt().ChartDataLabelCollection_set_DataLabelShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_set_DataLabelShapeType,self.Ptr, value.value)


    def Add(self)->'ChartDataLabel':
        """

        """
        GetDllLibPpt().ChartDataLabelCollection_Add.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_Add,self.Ptr)
        ret = None if intPtr==None else ChartDataLabel(intPtr)
        return ret



    def Remove(self ,value:'ChartDataLabel'):
        """
    <summary>
        Removes the first occurrence of a specific object from the collection.
    </summary>
    <param name="value">The DataLabel to remove from the collection.</param>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartDataLabelCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ChartDataLabelCollection_Remove,self.Ptr, intPtrvalue)


    def IndexOf(self ,value:'ChartDataLabel')->int:
        """
    <summary>
        Gets an index of the specified DataLabel in the collection.
    </summary>
    <param name="value">DataLabel to find.</param>
    <returns>Index of a DataLabel or -1 if DataLabel not from this collection.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().ChartDataLabelCollection_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_IndexOf,self.Ptr, intPtrvalue)
        return ret

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().ChartDataLabelCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartDataLabelCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartDataLabel(intPtr)
        return ret

    def get_Item(self ,index:int)->'ChartDataLabel':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.Charts.ChartDataLabel" />.
    </summary>
        """
        
        GetDllLibPpt().ChartDataLabelCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ChartDataLabelCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartDataLabel(intPtr)
        return ret


    @property

    def LeaderLines(self)->'IChartGridLine':
        """

        """
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLines.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_get_LeaderLines.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_get_LeaderLines,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
        """
        GetDllLibPpt().ChartDataLabelCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ChartDataLabelCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartDataLabelCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


