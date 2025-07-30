from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITable (IShape) :

    @dispatch
    def __getitem__(self, index):
        if(len(index) ==1):
            return self.TableRows[index[0]]
        if(len(index) ==2):
            column,row = index
            GetDllLibPpt().ITable_get_Item.argtypes=[c_void_p ,c_int,c_int]
            GetDllLibPpt().ITable_get_Item.restype=c_void_p
            intPtr = CallCFunction(GetDllLibPpt().ITable_get_Item,self.Ptr, column,row)
            ret = None if intPtr==None else Cell(intPtr)
            return ret


    @dispatch
    def get_Item(self ,column:int,row:int)->'Cell':
  
        GetDllLibPpt().ITable_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ITable_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Item,self.Ptr, column,row)
        ret = None if intPtr==None else Cell(intPtr)

    def MergeCells(self ,cell1:'Cell',cell2:'Cell',allowSplitting:bool):
        """
    <summary>
        Merges neighbour cells.
    </summary>
    <param name="cell1">Cell to merge.</param>
    <param name="cell2">Cell to merge.</param>
    <param name="allowSplitting">True to allow cells splitting.</param>
        """
        intPtrcell1:c_void_p = cell1.Ptr
        intPtrcell2:c_void_p = cell2.Ptr

        GetDllLibPpt().ITable_MergeCells.argtypes=[c_void_p ,c_void_p,c_void_p,c_bool]
        CallCFunction(GetDllLibPpt().ITable_MergeCells,self.Ptr, intPtrcell1,intPtrcell2,allowSplitting)


    def SetTableBorder(self ,borderType:'TableBorderType',borderWidth:float,borderColor:'Color'):
        """
    <summary>
        Setting up the table border
    </summary>
    <param name="borderType">border type</param>
    <param name="borderWidth">border width.</param>
    <param name="borderColor">border color.</param>
        """
        enumborderType:c_int = borderType.value
        intPtrborderColor:c_void_p = borderColor.Ptr

        GetDllLibPpt().ITable_SetTableBorder.argtypes=[c_void_p ,c_int,c_double,c_void_p]
        CallCFunction(GetDllLibPpt().ITable_SetTableBorder,self.Ptr, enumborderType,borderWidth,intPtrborderColor)

    @property

    def StylePreset(self)->'TableStylePreset':
        """
    <summary>
        Get's or sets builtin table style.
            Read/write <see cref="T:Spire.Presentation.TableStylePreset" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_StylePreset.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_StylePreset.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITable_get_StylePreset,self.Ptr)
        objwraped = TableStylePreset(ret)
        return objwraped

    @StylePreset.setter
    def StylePreset(self, value:'TableStylePreset'):
        GetDllLibPpt().ITable_set_StylePreset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITable_set_StylePreset,self.Ptr, value.value)

    @property

    def TableRows(self)->'TableRowCollection':
        """
    <summary>
        Gets the collectoin of rows.
            Read-only <see cref="T:Spire.Presentation.Collections.TableRowCollection" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_TableRows.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_TableRows.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_TableRows,self.Ptr)
        ret = None if intPtr==None else TableRowCollection(intPtr)
        return ret


    @property

    def ColumnsList(self)->'ColumnCollection':
        """
    <summary>
        Gets the collectoin of columns.
            Read-only <see cref="T:Spire.Presentation.Collections.ColumnCollection" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_ColumnsList.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ColumnsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_ColumnsList,self.Ptr)
        ret = None if intPtr==None else ColumnCollection(intPtr)
        return ret


    @property
    def RightToLeft(self)->bool:
        """
    <summary>
        Indicates whether the table has right to left reading order.
            Read-write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_RightToLeft.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_RightToLeft.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_RightToLeft,self.Ptr)
        return ret

    @RightToLeft.setter
    def RightToLeft(self, value:bool):
        GetDllLibPpt().ITable_set_RightToLeft.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_RightToLeft,self.Ptr, value)

    @property
    def FirstRow(self)->bool:
        """
    <summary>
        Indicates whether the first row of a table has to be drawn with a special formatting.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_FirstRow.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_FirstRow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_FirstRow,self.Ptr)
        return ret

    @FirstRow.setter
    def FirstRow(self, value:bool):
        GetDllLibPpt().ITable_set_FirstRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_FirstRow,self.Ptr, value)

    @property
    def FirstCol(self)->bool:
        """
    <summary>
        Indicates whether the first column of a table has to be drawn with a special formatting.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_FirstCol.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_FirstCol.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_FirstCol,self.Ptr)
        return ret

    @FirstCol.setter
    def FirstCol(self, value:bool):
        GetDllLibPpt().ITable_set_FirstCol.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_FirstCol,self.Ptr, value)

    @property
    def LastRow(self)->bool:
        """
    <summary>
        Indicates whether the last row of a table has to be drawn with a special formatting.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_LastRow.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_LastRow.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_LastRow,self.Ptr)
        return ret

    @LastRow.setter
    def LastRow(self, value:bool):
        GetDllLibPpt().ITable_set_LastRow.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_LastRow,self.Ptr, value)

    @property
    def LastCol(self)->bool:
        """
    <summary>
        Indicates whether the last column of a table has to be drawn with a special formatting.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_LastCol.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_LastCol.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_LastCol,self.Ptr)
        return ret

    @LastCol.setter
    def LastCol(self, value:bool):
        GetDllLibPpt().ITable_set_LastCol.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_LastCol,self.Ptr, value)

    @property
    def HorizontalBanding(self)->bool:
        """
    <summary>
        Indicates whether the even rows has to be drawn with a different formatting.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_HorizontalBanding.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_HorizontalBanding.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_HorizontalBanding,self.Ptr)
        return ret

    @HorizontalBanding.setter
    def HorizontalBanding(self, value:bool):
        GetDllLibPpt().ITable_set_HorizontalBanding.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_HorizontalBanding,self.Ptr, value)

    @property
    def VerticalBanding(self)->bool:
        """
    <summary>
        Indicates whether the even columns has to be drawn with a different formatting.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_VerticalBanding.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_VerticalBanding.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_VerticalBanding,self.Ptr)
        return ret

    @VerticalBanding.setter
    def VerticalBanding(self, value:bool):
        GetDllLibPpt().ITable_set_VerticalBanding.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_VerticalBanding,self.Ptr, value)

    @property

    def ShapeLocking(self)->'GraphicalNodeLocking':
        """
    <summary>
        Gets lock type of shape.
            Read-only <see cref="T:Spire.Presentation.Drawing.GraphicalNodeLocking" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else GraphicalNodeLocking(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
    <summary>
        Indicates whether the shape is Placeholder.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_IsPlaceholder,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
    <summary>
        Gets the placeholder for a shape.
            Read-only <see cref="P:Spire.Presentation.ITable.Placeholder" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Placeholder,self.Ptr)
        ret = None if intPtr==None else Placeholder(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
    <summary>
        Gets the shape's tags collection.
            Read-only <see cref="T:Spire.Presentation.Collections.TagCollection" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Frame(self)->'GraphicFrame':
        """
    <summary>
        Gets or sets the shape frame's properties.
            Read/write <see cref="T:Spire.Presentation.Drawing.GraphicFrame" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().ITable_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ITable_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat object that contains line formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.ITable.Line" />.
            Note: can return null for certain types of shapes which don't have line properties.
    </summary>
        """
        GetDllLibPpt().ITable_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
    <summary>
        Gets the ThreeDFormat object that 3d effect properties for a shape.
            Read-only <see cref="T:Spire.Presentation.Drawing.FormatThreeD" />.
            Note: can return null for certain types of shapes which don't have 3d properties.
    </summary>
        """
        GetDllLibPpt().ITable_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets the EffectFormat object which contains pixel effects applied to a shape.
            Read-only <see cref="P:Spire.Presentation.ITable.EffectDag" />
            Note: can return null for certain types of shapes which don't have effect properties.
    </summary>
        """
        GetDllLibPpt().ITable_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets the FillFormat object that contains fill formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.ITable.Fill" />.
            Note: can return null for certain types of shapes which don't have fill properties.
    </summary>
        """
        GetDllLibPpt().ITable_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Click(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse click.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().ITable_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ITable_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse over.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().ITable_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ITable_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
    <summary>
        Indicates whether the shape is hidden.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ITable_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().ITable_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ITable_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
    <summary>
        Gets or sets the position of a shape in the z-order.
            Shapes[0] returns the shape at the back of the z-order,
            and Shapes[Shapes.Count - 1] returns the shape at the front of the z-order.
            Read/Write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ITable_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().ITable_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ITable_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
    <summary>
        Gets or sets the number of degrees the specified shape is rotated around
            the z-axis. A positive value indicates clockwise rotation; a negative value
            indicates counterclockwise rotation.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().ITable_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
    <summary>
        Gets or sets the x-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().ITable_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
        Gets or sets the y-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().ITable_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
    <summary>
        Gets or sets the width of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ITable_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Gets or sets the height of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITable_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ITable_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITable_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
    <summary>
        Gets or sets the alternative text associated with a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ITable_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITable_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITable_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the name of a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ITable_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ITable_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ITable_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().ITable_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().ITable_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ITable_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def get_Item(self ,columnIndex:int,rowIndex:int)->'Cell':
        """
    <summary>
        Gets the cell at the specified column and row indexes.
            Read-only <see cref="T:Spire.Presentation.Cell" />.
    </summary>
        """
        
        GetDllLibPpt().ITable_get_Item.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ITable_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITable_get_Item,self.Ptr, columnIndex,rowIndex)
        ret = None if intPtr==None else Cell(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
    <summary>
        Removes placeholder from the shape.
    </summary>
        """
        GetDllLibPpt().ITable_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ITable_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().ITable_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ITable_Dispose,self.Ptr)


    def DistributeRows(self ,startRowIndex:int,endRowIndex:int):
        """
    <summary>
        distribute rows.
    </summary>
    <param name="startRowIndex">start row index.</param>
    <param name="endRowIndex">end row index.</param>
        """
        
        GetDllLibPpt().ITable_DistributeRows.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().ITable_DistributeRows,self.Ptr, startRowIndex,endRowIndex)


    def DistributeColumns(self ,startColumnIndex:int,endColumnIndex:int):
        """
    <summary>
        distribute columns.
    </summary>
    <param name="startColumnIndex">start column index.</param>
    <param name="endColumnIndex">end column index.</param>
        """
        
        GetDllLibPpt().ITable_DistributeColumns.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().ITable_DistributeColumns,self.Ptr, startColumnIndex,endColumnIndex)

