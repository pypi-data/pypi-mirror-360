from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IOleObject (SpireObject) :
    """

    """
    @property

    def SubstituteImagePictureFillFormat(self)->'PictureFillFormat':
        """
    <summary>
        Gets OleObject image fill properties object.
            Readonly <see cref="T:Spire.Presentation.Drawing.PictureFillFormat" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_SubstituteImagePictureFillFormat.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_SubstituteImagePictureFillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_SubstituteImagePictureFillFormat,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def ObjectName(self)->str:
        """
    <summary>
        Gets or sets the name of an object.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_ObjectName.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_ObjectName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IOleObject_get_ObjectName,self.Ptr))
        return ret


    @ObjectName.setter
    def ObjectName(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IOleObject_set_ObjectName.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_ObjectName,self.Ptr,valuePtr)

    @property

    def ProgId(self)->str:
        """
    <summary>
        Gets or sets the ProgID of an object.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_ProgId.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_ProgId.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IOleObject_get_ProgId,self.Ptr))
        return ret


    @ProgId.setter
    def ProgId(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IOleObject_set_ProgId.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_ProgId,self.Ptr,valuePtr)

    @property

    def Data(self)->'Stream':
        """
    <summary>
        Gets or sets embedded object as byte array.
            Read/write <see cref="T:System.Byte" />[].
    </summary>
        """
        GetDllLibPpt().IOleObject_get_DataStream.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_DataStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_DataStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @Data.setter
    def Data(self, value:'Stream'):
       
        GetDllLibPpt().IOleObject_set_DataStream.argtypes=[c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_DataStream,self.Ptr, value.Ptr)


    @property

    def LinkShortFilePath(self)->str:
        """
    <summary>
        Gets the full path to a linked file. 
            Read-only <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_LinkShortFilePath.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_LinkShortFilePath.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IOleObject_get_LinkShortFilePath,self.Ptr))
        return ret


    @property

    def LinkFilePath(self)->str:
        """
    <summary>
        Gets the full path to a linked file. 
            Read-only <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_LinkFilePath.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_LinkFilePath.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IOleObject_get_LinkFilePath,self.Ptr))
        return ret


    @LinkFilePath.setter
    def LinkFilePath(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IOleObject_set_LinkFilePath.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_LinkFilePath,self.Ptr,valuePtr)

    @property
    def IsIconVisible(self)->bool:
        """
    <summary>
        Indicates whether an object is visible as icon.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_IsIconVisible.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_IsIconVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_IsIconVisible,self.Ptr)
        return ret

    @IsIconVisible.setter
    def IsIconVisible(self, value:bool):
        GetDllLibPpt().IOleObject_set_IsIconVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IOleObject_set_IsIconVisible,self.Ptr, value)

    @property
    def IsObjectLink(self)->bool:
        """
    <summary>
        Indicates whether an object is linked to external file.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_IsObjectLink.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_IsObjectLink.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_IsObjectLink,self.Ptr)
        return ret

    @property

    def ShapeLocking(self)->'GraphicalNodeLocking':
        """
    <summary>
        Gets lock type of shape.
            Read-only <see cref="T:Spire.Presentation.Drawing.GraphicalNodeLocking" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else GraphicalNodeLocking(intPtr)
        return ret


    @property
    def IsTextBox(self)->bool:
        """
    <summary>
        Indicates whether the shape is TextHolder.
            Read-only <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_IsTextBox.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_IsTextBox.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_IsTextBox,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
    <summary>
        Gets the placeholder for a shape.
            Read-only <see cref="P:Spire.Presentation.IOleObject.Placeholder" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Placeholder,self.Ptr)
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
        GetDllLibPpt().IOleObject_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_TagsList,self.Ptr)
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
        GetDllLibPpt().IOleObject_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().IOleObject_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat object that contains line formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IOleObject.Line" />.
            Note: can return null for certain types of shapes which don't have line properties.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Line,self.Ptr)
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
        GetDllLibPpt().IOleObject_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets the EffectFormat object which contains pixel effects applied to a shape.
            Read-only <see cref="P:Spire.Presentation.IOleObject.EffectDag" />
            Note: can return null for certain types of shapes which don't have effect properties.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets the FillFormat object that contains fill formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IOleObject.Fill" />.
            Note: can return null for certain types of shapes which don't have fill properties.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Fill,self.Ptr)
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
        GetDllLibPpt().IOleObject_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().IOleObject_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse over.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().IOleObject_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
    <summary>
        Indicates whether the shape is hidden.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().IOleObject_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IOleObject_set_IsHidden,self.Ptr, value)

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
        GetDllLibPpt().IOleObject_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().IOleObject_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IOleObject_set_ZOrderPosition,self.Ptr, value)

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
        GetDllLibPpt().IOleObject_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().IOleObject_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IOleObject_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
    <summary>
        Gets or sets the x-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().IOleObject_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IOleObject_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
        Gets or sets the y-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().IOleObject_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IOleObject_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
    <summary>
        Gets or sets the width of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IOleObject_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IOleObject_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Gets or sets the height of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IOleObject_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().IOleObject_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IOleObject_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
    <summary>
        Gets or sets the alternative text associated with a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IOleObject_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IOleObject_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the name of a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IOleObject_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IOleObject_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IOleObject_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().IOleObject_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
    <summary>
        Reference to Parent object. Read-only.
    </summary>
        """
        GetDllLibPpt().IOleObject_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IOleObject_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IOleObject_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
    <summary>
        Removes placeholder from the shape.
    </summary>
        """
        GetDllLibPpt().IOleObject_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IOleObject_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().IOleObject_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IOleObject_Dispose,self.Ptr)

