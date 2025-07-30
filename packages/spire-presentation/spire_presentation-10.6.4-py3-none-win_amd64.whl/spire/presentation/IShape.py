from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IShape (SpireObject) :
    """

    """
    @property
    def IsPlaceholder(self)->bool:
        """
    <summary>
        Indicates whether the shape is Placeholder.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IShape_get_IsPlaceholder,self.Ptr)
        return ret

    @property
    def IsTextBox(self)->bool:
        """
    <summary>
        Indicates whether the shape is TextBox.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_IsTextBox.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_IsTextBox.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IShape_get_IsTextBox,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
    <summary>
        Gets the placeholder for a shape.
            Read-only <see cref="P:Spire.Presentation.IShape.Placeholder" />.
    </summary>
        """
        
        GetDllLibPpt().IShape_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Placeholder,self.Ptr)
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
        GetDllLibPpt().IShape_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_TagsList,self.Ptr)
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
        GetDllLibPpt().IShape_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().IShape_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IShape_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat object that contains line formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IShape.Line" />.
            Note: can return null for certain types of shapes which don't have line properties.
    </summary>
        """
        GetDllLibPpt().IShape_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Line,self.Ptr)
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
        GetDllLibPpt().IShape_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets the EffectFormat object which contains pixel effects applied to a shape.
            Read-only <see cref="P:Spire.Presentation.IShape.EffectDag" />
            Note: can return null for certain types of shapes which don't have effect properties.
    </summary>
        """
        GetDllLibPpt().IShape_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets the FillFormat object that contains fill formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IShape.Fill" />.
            Note: can return null for certain types of shapes which don't have fill properties.
    </summary>
        """
        GetDllLibPpt().IShape_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Fill,self.Ptr)
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
        GetDllLibPpt().IShape_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().IShape_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IShape_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse over.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().IShape_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IShape_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
    <summary>
        Indicates whether the shape is hidden.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IShape_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().IShape_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IShape_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IShape_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Parent,self.Ptr)
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
        GetDllLibPpt().IShape_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IShape_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().IShape_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IShape_set_ZOrderPosition,self.Ptr, value)

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
        GetDllLibPpt().IShape_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().IShape_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
    <summary>
        Gets or sets the x-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().IShape_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
        Gets or sets the y-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().IShape_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
    <summary>
        Gets or sets the width of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IShape_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Gets or sets the height of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IShape_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().IShape_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IShape_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
    <summary>
        Gets or sets the alternative text associated with a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IShape_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IShape_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IShape_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def AlternativeTitle(self)->str:
        """
    <summary>
        Gets or sets the alternative title associated with a shape.
            Read/write <see cref="T:System.String" /></summary>
        """
        GetDllLibPpt().IShape_get_AlternativeTitle.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_AlternativeTitle.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IShape_get_AlternativeTitle,self.Ptr))
        return ret


    @AlternativeTitle.setter
    def AlternativeTitle(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IShape_set_AlternativeTitle.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IShape_set_AlternativeTitle,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the name of a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IShape_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IShape_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IShape_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IShape_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IShape_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        from spire.presentation import Presentation
        GetDllLibPpt().IShape_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
    <summary>
        Removes placeholder from the shape.
    </summary>
        """
        GetDllLibPpt().IShape_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IShape_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().IShape_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IShape_Dispose,self.Ptr)


    def SetShapeAlignment(self ,shapeAlignment:'ShapeAlignment'):
        """
    <summary>
        Sets the alignment with a shape.
    </summary>
        """
        enumshapeAlignment:c_int = shapeAlignment.value

        GetDllLibPpt().IShape_SetShapeAlignment.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_SetShapeAlignment,self.Ptr, enumshapeAlignment)


    def SetShapeArrange(self ,shapeArrange:'ShapeArrange'):
        """
    <summary>
        Sets the arrangement with a shape.
    </summary>
        """
        enumshapeArrange:c_int = shapeArrange.value

        GetDllLibPpt().IShape_SetShapeArrange.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_SetShapeArrange,self.Ptr, enumshapeArrange)


    def InsertVideo(self ,filepath:str):
        """
    <summary>
        Insert a video into placeholder shape.
    </summary>
    <param name="filepath">Video file path</param>
        """
        
        filepathPtr = StrToPtr(filepath)
        GetDllLibPpt().IShape_InsertVideo.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IShape_InsertVideo,self.Ptr,filepathPtr)


    def InsertSmartArt(self ,smartArtLayoutType:'SmartArtLayoutType'):
        """
    <summary>
        Insert a smartArt into placeholder shape.
    </summary>
    <param name="type">smartArt Type</param>
        """
        enumsmartArtLayoutType:c_int = smartArtLayoutType.value

        GetDllLibPpt().IShape_InsertSmartArt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_InsertSmartArt,self.Ptr, enumsmartArtLayoutType)


    def InsertChart(self ,type:'ChartType'):
        """
    <summary>
        Insert a chart into placeholder shape.
    </summary>
    <param name="type">Chart Type</param>
        """
        enumtype:c_int = type.value

        GetDllLibPpt().IShape_InsertChart.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IShape_InsertChart,self.Ptr, enumtype)


    def InsertTable(self ,tableColumnCount:int,tableRowCount:int):
        """
    <summary>
        Insert a table into placeholder shape.
    </summary>
    <param name="tableColumnCount">Tablecolumn count</param>
    <param name="tableRowCount">Tablerow count</param>
        """
        
        GetDllLibPpt().IShape_InsertTable.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().IShape_InsertTable,self.Ptr, tableColumnCount,tableRowCount)

    @dispatch

    def InsertPicture(self ,stream:Stream):
        """
    <summary>
        Insert a picture into placeholder shape from stream.
    </summary>
    <param name="stream">the picture stream</param>
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().IShape_InsertPicture.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().IShape_InsertPicture,self.Ptr, intPtrstream)

    @dispatch

    def InsertPicture(self ,filepath:str):
        """
    <summary>
        Insert a picture into placeholder shape.
    </summary>
    <param name="filepath">Picture file path</param>
        """
        
        filepathPtr = StrToPtr(filepath)
        GetDllLibPpt().IShape_InsertPictureF.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IShape_InsertPictureF,self.Ptr,filepathPtr)

    @property

    def Id(self)->'int':
        """

        """
        GetDllLibPpt().IShape_get_Id.argtypes=[c_void_p]
        GetDllLibPpt().IShape_get_Id.restype=c_int
        shapeId = CallCFunction(GetDllLibPpt().IShape_get_Id,self.Ptr)
        #ret = None if intPtr==None else UInt32(intPtr)
        return shapeId



    def ReplaceTextWithRegex(self ,regex:'Regex',newValue:str):
        """
    <summary>
        Replace text in shape with regex.
    </summary>
        """
        intPtrregex:c_void_p = regex.Ptr

        newValuePtr = StrToPtr(newValue)
        GetDllLibPpt().IShape_ReplaceTextWithRegex.argtypes=[c_void_p ,c_void_p,c_char_p]
        CallCFunction(GetDllLibPpt().IShape_ReplaceTextWithRegex,self.Ptr, intPtrregex,newValuePtr)



    def SaveAsImage(self)->'Stream':
        """
    <summary>
        Save shape to Image.
    </summary>
    <returns></returns>
        """
        GetDllLibPpt().IShape_SaveAsImage.argtypes=[c_void_p]
        GetDllLibPpt().IShape_SaveAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_SaveAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    def SaveAsSvg(self)->'Stream':
        """
    <summary>
        Save the shape to SVG format.
    </summary>
    <returns>A byte array of SVG file-stream.</returns>
        """
        GetDllLibPpt().IShape_SaveAsSvg.argtypes=[c_void_p]
        GetDllLibPpt().IShape_SaveAsSvg.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_SaveAsSvg,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret

    def SaveAsSvgInSlide(self)->'Stream':
        """
    <summary>
        Save the shape to SVG format.
    </summary>
    <returns>A byte array of SVG file-stream.</returns>
        """
        GetDllLibPpt().IShape_SaveAsSvgInSlide.argtypes=[c_void_p]
        GetDllLibPpt().IShape_SaveAsSvgInSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IShape_SaveAsSvgInSlide,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret
