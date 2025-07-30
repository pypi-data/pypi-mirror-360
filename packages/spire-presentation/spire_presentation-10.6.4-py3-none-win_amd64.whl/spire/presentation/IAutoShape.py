from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class IAutoShape (IShape) :
    """

    """
    @property

    def Locking(self)->'ShapeLocking':
        """
    <summary>
        Gets shape's locks.
            Read-only <see cref="P:Spire.Presentation.IAutoShape.Locking" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Locking.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Locking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Locking,self.Ptr)
        ret = None if intPtr==None else ShapeLocking(intPtr)
        return ret


    @property

    def TextFrame(self)->'ITextFrameProperties':
        """
    <summary>
        Gets TextFrame object for the AutoShape.
            Read-only <see cref="T:Spire.Presentation.TextFrameProperties" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property
    def UseBackgroundFill(self)->bool:
        """
    <summary>
        Indicates whether this autoshape should be filled with slide's background fill instead of specified by style or fill format.
            Read/write bool.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_UseBackgroundFill.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_UseBackgroundFill.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_UseBackgroundFill,self.Ptr)
        return ret

    @UseBackgroundFill.setter
    def UseBackgroundFill(self, value:bool):
        GetDllLibPpt().IAutoShape_set_UseBackgroundFill.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAutoShape_set_UseBackgroundFill,self.Ptr, value)

    @property

    def ShapeStyle(self)->'ShapeStyle':
        """

        """
        GetDllLibPpt().IAutoShape_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """

        """
        GetDllLibPpt().IAutoShape_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        GetDllLibPpt().IAutoShape_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAutoShape_set_ShapeType,self.Ptr, value.value)

    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """

        """
        GetDllLibPpt().IAutoShape_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Adjustments,self.Ptr)
        ret = None if intPtr==None else ShapeAdjustCollection(intPtr)
        return ret


    @property
    def IsPlaceholder(self)->bool:
        """
    <summary>
        Indicates whether the shape is Placeholder.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_IsPlaceholder,self.Ptr)
        return ret

    @property
    def IsTextBox(self)->bool:
        """
    <summary>
        Indicates whether the shape is TextBox.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_IsTextBox.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_IsTextBox.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_IsTextBox,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
    <summary>
        Gets the placeholder for a shape.
            Read-only <see cref="P:Spire.Presentation.IAutoShape.Placeholder" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Placeholder,self.Ptr)
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
        GetDllLibPpt().IAutoShape_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_TagsList,self.Ptr)
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
        GetDllLibPpt().IAutoShape_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().IAutoShape_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat object that contains line formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IAutoShape.Line" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ThreeD(self)->'FormatThreeD':
        """
    <summary>
        Gets the ThreeDFormat object that 3d effect properties for a shape.
            Read-only <see cref="T:Spire.Presentation.Drawing.FormatThreeD" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets the EffectFormat object which contains pixel effects applied to a shape.
            Read-only <see cref="P:Spire.Presentation.IAutoShape.EffectDag" />
            Note: can return null for certain types of shapes which don't have effect properties.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets the FillFormat object that contains fill formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IAutoShape.Fill" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Fill,self.Ptr)
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
        GetDllLibPpt().IAutoShape_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().IAutoShape_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse over.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().IAutoShape_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
    <summary>
        Indicates whether the shape is hidden.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().IAutoShape_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IAutoShape_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Parent,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property
    def ZOrderPosition(self)->int:
        """
    <summary>
        Gets or sets the position of a shape in the z-order.
            Read/Write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().IAutoShape_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IAutoShape_set_ZOrderPosition,self.Ptr, value)

    @property
    def Rotation(self)->float:
        """
    <summary>
        Gets or sets the number of degrees the specified shape is rotated.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().IAutoShape_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
    <summary>
        Gets or sets the x-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().IAutoShape_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
        Gets or sets the y-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().IAutoShape_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
    <summary>
        Gets or sets the width of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IAutoShape_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Gets or sets the height of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().IAutoShape_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
    <summary>
        Gets or sets the alternative text associated with a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAutoShape_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IAutoShape_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the name of a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAutoShape_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IAutoShape_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IAutoShape_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        from spire.presentation import ActiveSlide
        GetDllLibPpt().IAutoShape_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        from spire.presentation import Presentation
        GetDllLibPpt().IAutoShape_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAutoShape_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property
    def ContainMathEquation(self)->bool:
        """
    <summary>
        if shape contains math equation.
    </summary>
        """
        GetDllLibPpt().IAutoShape_get_ContainMathEquation.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_ContainMathEquation.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IAutoShape_get_ContainMathEquation,self.Ptr)
        return ret


    def AppendTextFrame(self ,text:str):
        """
    <summary>
        Adds a new TextFrame to a shape.
            If shape already has TextFrame then simply changes its text.
    </summary>
    <param name="text">Default text for a new TextFrame.</param>
        """
        
        textPtr = StrToPtr(text)
        GetDllLibPpt().IAutoShape_AppendTextFrame.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IAutoShape_AppendTextFrame,self.Ptr,textPtr)

    def RemovePlaceholder(self):
        """
    <summary>
        Removes placeholder from the shape.
    </summary>
        """
        GetDllLibPpt().IAutoShape_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().IAutoShape_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IAutoShape_Dispose,self.Ptr)

    @property
    def Points(self)->List['PointF']:
        """

        """
        GetDllLibPpt().IAutoShape_get_Points.argtypes=[c_void_p]
        GetDllLibPpt().IAutoShape_get_Points.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().IAutoShape_get_Points,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, PointF)
        return ret

