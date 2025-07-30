from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Cell (  IActiveSlide, IActivePresentation) :
    """
    <summary>
        Represents a cell of a table.
    </summary>
    """
    @property
    def OffsetX(self)->float:
        """
    <summary>
        Gets a distance from left side of a table to left side of a cell.
            Read-only <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_OffsetX.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_OffsetX.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_OffsetX,self.Ptr)
        return ret

    @property
    def OffsetY(self)->float:
        """
    <summary>
        Gets a distance from top side of a table to top side of a cell.
            Read-only <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_OffsetY.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_OffsetY.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_OffsetY,self.Ptr)
        return ret

    @property
    def FirstRowIndex(self)->int:
        """
    <summary>
        Gets an index of first row, covered by the cell.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_FirstRowIndex.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_FirstRowIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_FirstRowIndex,self.Ptr)
        return ret

    @property
    def FirstColumnIndex(self)->int:
        """
    <summary>
        Gets an index of first column, covered by the cell.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_FirstColumnIndex.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_FirstColumnIndex.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_FirstColumnIndex,self.Ptr)
        return ret

    @property
    def Width(self)->float:
        """
    <summary>
        Gets the width of the cell.
            Read-only <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_Width,self.Ptr)
        return ret

    @property
    def Height(self)->float:
        """
    <summary>
        Gets the height of the cell.
            Read-only <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Height.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_Height,self.Ptr)
        return ret

    @property
    def MinimalHeight(self)->float:
        """
    <summary>
        Gets the minimum height of a cell.
            This is a sum of minimal heights of all rows cowered by the cell.
            Read-only <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_MinimalHeight.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MinimalHeight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MinimalHeight,self.Ptr)
        return ret

    @property

    def BorderLeft(self)->'TextLineFormat':
        """
    <summary>
        Gets a left border line properties object.
            Read-only <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderLeft.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderLeft.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderLeft,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderTop(self)->'TextLineFormat':
        """
    <summary>
        Gets a top border line properties object.
            Read-only <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderTop.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderTop.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderTop,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderRight(self)->'TextLineFormat':
        """
    <summary>
        Gets a right border line properties object.
            Read-only <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderRight.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderRight.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderRight,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderBottom(self)->'TextLineFormat':
        """
    <summary>
        Gets a bottom border line properties object.
            Read-only <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderBottom.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderBottom.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderBottom,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderLeftDisplayColor(self)->'Color':
        """
    <summary>
        Gets a left border display color.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderLeftDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderLeftDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderLeftDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderTopDisplayColor(self)->'Color':
        """
    <summary>
        Gets a top border display color.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderTopDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderTopDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderTopDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderRightDisplayColor(self)->'Color':
        """
    <summary>
        Gets a right border display color.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderRightDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderRightDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderRightDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderBottomDisplayColor(self)->'Color':
        """
    <summary>
        Gets a bottom border display color.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderBottomDisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderBottomDisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderBottomDisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @property

    def BorderDiagonalDown(self)->'TextLineFormat':
        """
    <summary>
        Gets a top-left to bottom-right diagonal line properties object.
            Read-only <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderDiagonalDown.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderDiagonalDown.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderDiagonalDown,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def BorderDiagonalUp(self)->'TextLineFormat':
        """
    <summary>
        Gets a bottom-left to top-right diagonal line properties object.
            Read-only <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_BorderDiagonalUp.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_BorderDiagonalUp.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_BorderDiagonalUp,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def FillFormat(self)->'FillFormat':
        """
    <summary>
        Gets a cell fill properties object.
            Read-only <see cref="P:Spire.Presentation.Cell.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property
    def MarginLeft(self)->float:
        """
    <summary>
        Gets or sets the left margin in a TextFrame.
            Read/write <see cref="T:System.Double" />. 
    </summary>
        """
        GetDllLibPpt().Cell_get_MarginLeft.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginLeft.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginLeft,self.Ptr)
        return ret

    @MarginLeft.setter
    def MarginLeft(self, value:float):
        GetDllLibPpt().Cell_set_MarginLeft.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginLeft,self.Ptr, value)

    @property
    def MarginRight(self)->float:
        """
    <summary>
        Gets or sets the right margin in a TextFrame.
            Read/write <see cref="T:System.Double" />. 
    </summary>
        """
        GetDllLibPpt().Cell_get_MarginRight.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginRight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginRight,self.Ptr)
        return ret

    @MarginRight.setter
    def MarginRight(self, value:float):
        GetDllLibPpt().Cell_set_MarginRight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginRight,self.Ptr, value)

    @property
    def MarginTop(self)->float:
        """
    <summary>
        Gets or sets the top margin in a TextFrame.
            Read/write <see cref="T:System.Double" />. 
    </summary>
        """
        GetDllLibPpt().Cell_get_MarginTop.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginTop.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginTop,self.Ptr)
        return ret

    @MarginTop.setter
    def MarginTop(self, value:float):
        GetDllLibPpt().Cell_set_MarginTop.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginTop,self.Ptr, value)

    @property
    def MarginBottom(self)->float:
        """
    <summary>
        Gets or sets the bottom margin in a TextFrame.
            Read/write <see cref="T:System.Double" />. 
    </summary>
        """
        GetDllLibPpt().Cell_get_MarginBottom.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_MarginBottom.restype=c_double
        ret = CallCFunction(GetDllLibPpt().Cell_get_MarginBottom,self.Ptr)
        return ret

    @MarginBottom.setter
    def MarginBottom(self, value:float):
        GetDllLibPpt().Cell_set_MarginBottom.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().Cell_set_MarginBottom,self.Ptr, value)

    @property

    def VerticalTextType(self)->'VerticalTextType':
        """
    <summary>
        Gets or sets the type of vertical text.
            Read/write <see cref="P:Spire.Presentation.Cell.VerticalTextType" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_VerticalTextType.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_VerticalTextType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_VerticalTextType,self.Ptr)
        objwraped = VerticalTextType(ret)
        return objwraped

    @VerticalTextType.setter
    def VerticalTextType(self, value:'VerticalTextType'):
        GetDllLibPpt().Cell_set_VerticalTextType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Cell_set_VerticalTextType,self.Ptr, value.value)

    @property

    def TextAnchorType(self)->'TextAnchorType':
        """
    <summary>
        Gets or sets the text anchor type.
            Read/write <see cref="P:Spire.Presentation.Cell.TextAnchorType" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_TextAnchorType.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_TextAnchorType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_TextAnchorType,self.Ptr)
        objwraped = TextAnchorType(ret)
        return objwraped

    @TextAnchorType.setter
    def TextAnchorType(self, value:'TextAnchorType'):
        GetDllLibPpt().Cell_set_TextAnchorType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Cell_set_TextAnchorType,self.Ptr, value.value)

    @property
    def AnchorCenter(self)->bool:
        """
    <summary>
        Indicates whether or not text box centered inside a cell.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_AnchorCenter.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_AnchorCenter.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Cell_get_AnchorCenter,self.Ptr)
        return ret

    @AnchorCenter.setter
    def AnchorCenter(self, value:bool):
        GetDllLibPpt().Cell_set_AnchorCenter.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Cell_set_AnchorCenter,self.Ptr, value)

    @property
    def ColSpan(self)->int:
        """
    <summary>
        Gets the number of grid columns in the parent table's table grid
            which shall be spanned by the current cell. This property allows cells
            to have the appearance of being merged, as they span vertical boundaries
            of other cells in the table.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_ColSpan.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_ColSpan.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_ColSpan,self.Ptr)
        return ret

    @property
    def RowSpan(self)->int:
        """
    <summary>
        Gets the number of rows that a merged cell spans. This is used in combination
            with the vMerge attribute on other cells in order to specify the beginning cell
            of a horizontal merge.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_RowSpan.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_RowSpan.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Cell_get_RowSpan,self.Ptr)
        return ret

    @property

    def TextFrame(self)->'ITextFrameProperties':
        """
    <summary>
        Gets the text frame of a cell.
            Read-only <see cref="T:Spire.Presentation.TextFrameProperties" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a cell.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().Cell_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
    <summary>
        Gets the parent presentation of a cell.
            Read-only <see cref="T:Spire.Presentation.PresentationPptx" />.
    </summary>
        """
        from spire.presentation import Presentation
        GetDllLibPpt().Cell_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret



    def Split(self ,RowCount:int,ColunmCount:int):
        """
    <summary>
        Split the cell.
    </summary>
    <param name="RowCount">The number of cells being split in the row direction.</param>
    <param name="ColunmCount">The number of cells being split in the colunm direction.</param>
        """
        
        GetDllLibPpt().Cell_Split.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().Cell_Split,self.Ptr, RowCount,ColunmCount)

    def SplitBySpan(self):
        """
    <summary>
        The cell is split into its RowSpan rows in the  row direction,
            and it is split into its ColSpan colunms in the colunm direction.
    </summary>
        """
        GetDllLibPpt().Cell_SplitBySpan.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Cell_SplitBySpan,self.Ptr)

    @property

    def DisplayColor(self)->'Color':
        """
    <summary>
        get cell's display color
    </summary>
        """
        GetDllLibPpt().Cell_get_DisplayColor.argtypes=[c_void_p]
        GetDllLibPpt().Cell_get_DisplayColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Cell_get_DisplayColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


