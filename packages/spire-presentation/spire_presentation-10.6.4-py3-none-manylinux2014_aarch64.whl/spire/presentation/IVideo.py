from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IVideo (  IShape) :
    """

    """
    @property

    def EmbedImage(self)->'IImageData':
        """
    <summary>
        Gets or sets an Video image.
            Read/write <see cref="P:Spire.Presentation.IVideo.EmbedImage" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_EmbedImage.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_EmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_EmbedImage,self.Ptr)
        ret = None if intPtr==None else IImageData(intPtr)
        return ret


    @EmbedImage.setter
    def EmbedImage(self, value:'IImageData'):
        GetDllLibPpt().IVideo_set_EmbedImage.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_EmbedImage,self.Ptr, value.Ptr)

    @property
    def RewindVideo(self)->bool:
        """
    <summary>
        Indicates whether a video is automatically rewinded to start
            as soon as the movie has finished playing.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_RewindVideo.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_RewindVideo.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_RewindVideo,self.Ptr)
        return ret

    @RewindVideo.setter
    def RewindVideo(self, value:bool):
        GetDllLibPpt().IVideo_set_RewindVideo.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_RewindVideo,self.Ptr, value)

    @property
    def PlayLoopMode(self)->bool:
        """
    <summary>
        Indicates whether an audio is looped.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_PlayLoopMode.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_PlayLoopMode.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_PlayLoopMode,self.Ptr)
        return ret

    @PlayLoopMode.setter
    def PlayLoopMode(self, value:bool):
        GetDllLibPpt().IVideo_set_PlayLoopMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_PlayLoopMode,self.Ptr, value)

    @property
    def HideAtShowing(self)->bool:
        """
    <summary>
        Indicates whether an AudioFrame is hidden.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_HideAtShowing.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_HideAtShowing.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_HideAtShowing,self.Ptr)
        return ret

    @HideAtShowing.setter
    def HideAtShowing(self, value:bool):
        GetDllLibPpt().IVideo_set_HideAtShowing.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_HideAtShowing,self.Ptr, value)

    @property

    def Volume(self)->'AudioVolumeType':
        """
    <summary>
        Gets or sets the audio volume.
            Read/write <see cref="T:Spire.Presentation.AudioVolumeType" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Volume.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Volume.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Volume,self.Ptr)
        objwraped = AudioVolumeType(ret)
        return objwraped

    @Volume.setter
    def Volume(self, value:'AudioVolumeType'):
        GetDllLibPpt().IVideo_set_Volume.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_Volume,self.Ptr, value.value)

    @property

    def PlayMode(self)->'VideoPlayMode':
        """
    <summary>
        Gets or sets the video play mode.
            Read/write <see cref="T:Spire.Presentation.VideoPlayMode" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_PlayMode.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_PlayMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_PlayMode,self.Ptr)
        objwraped = VideoPlayMode(ret)
        return objwraped

    @PlayMode.setter
    def PlayMode(self, value:'VideoPlayMode'):
        GetDllLibPpt().IVideo_set_PlayMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_PlayMode,self.Ptr, value.value)

    @property
    def FullScreenMode(self)->bool:
        """
    <summary>
        Indicates whether a video is shown in full screen mode.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_FullScreenMode.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_FullScreenMode.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_FullScreenMode,self.Ptr)
        return ret

    @FullScreenMode.setter
    def FullScreenMode(self, value:bool):
        GetDllLibPpt().IVideo_set_FullScreenMode.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_FullScreenMode,self.Ptr, value)

    @property

    def LinkPathLong(self)->str:
        """
    <summary>
        Gets or sets the name of an audio file which is linked to a VideoFrame.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_LinkPathLong.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_LinkPathLong.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IVideo_get_LinkPathLong,self.Ptr))
        return ret


    @LinkPathLong.setter
    def LinkPathLong(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IVideo_set_LinkPathLong.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IVideo_set_LinkPathLong,self.Ptr,valuePtr)

    @property

    def EmbeddedVideoData(self)->'VideoData':
        """
    <summary>
        Gets or sets embedded video object.
            Read/write <see cref="T:Spire.Presentation.VideoData" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_EmbeddedVideoData.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_EmbeddedVideoData.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_EmbeddedVideoData,self.Ptr)
        ret = None if intPtr==None else VideoData(intPtr)
        return ret


    @EmbeddedVideoData.setter
    def EmbeddedVideoData(self, value:'VideoData'):
        GetDllLibPpt().IVideo_set_EmbeddedVideoData.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_EmbeddedVideoData,self.Ptr, value.Ptr)

    @property

    def ShapeLocking(self)->'SlidePictureLocking':
        """
    <summary>
        Gets shape's locks.
            Readonly <see cref="T:Spire.Presentation.SlidePictureLocking" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else SlidePictureLocking(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """
    <summary>
        Returns or sets the AutoShape type.
    </summary>
        """
        GetDllLibPpt().IVideo_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        GetDllLibPpt().IVideo_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_ShapeType,self.Ptr, value.value)

    @property

    def PictureFill(self)->'PictureFillFormat':
        """
    <summary>
        Gets the PictureFillFormat object.
            Read-only <see cref="T:Spire.Presentation.Drawing.PictureFillFormat" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def ShapeStyle(self)->'ShapeStyle':
        """
    <summary>
        Gets shape's style object.
            Read-only <see cref="P:Spire.Presentation.IVideo.ShapeStyle" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """
    <summary>
        Gets a collection of shape's adjustment values.
            Readonly <see cref="T:Spire.Presentation.Collections.ShapeAdjustCollection" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Adjustments,self.Ptr)
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
        GetDllLibPpt().IVideo_get_IsPlaceholder.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_IsPlaceholder.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_IsPlaceholder,self.Ptr)
        return ret

    @property

    def Placeholder(self)->'Placeholder':
        """
    <summary>
        Gets the placeholder for a shape.
            Read-only <see cref="P:Spire.Presentation.IVideo.Placeholder" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Placeholder.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Placeholder.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Placeholder,self.Ptr)
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
        GetDllLibPpt().IVideo_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_TagsList,self.Ptr)
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
        GetDllLibPpt().IVideo_get_Frame.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Frame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Frame,self.Ptr)
        ret = None if intPtr==None else GraphicFrame(intPtr)
        return ret


    @Frame.setter
    def Frame(self, value:'GraphicFrame'):
        GetDllLibPpt().IVideo_set_Frame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_Frame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat object that contains line formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IVideo.Line" />.
            Note: can return null for certain types of shapes which don't have line properties.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Line,self.Ptr)
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
        GetDllLibPpt().IVideo_get_ThreeD.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_ThreeD,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets the EffectFormat object which contains pixel effects applied to a shape.
            Read-only <see cref="P:Spire.Presentation.IVideo.EffectDag" />
            Note: can return null for certain types of shapes which don't have effect properties.
    </summary>
        """
        GetDllLibPpt().IVideo_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets the FillFormat object that contains fill formatting properties for a shape.
            Read-only <see cref="P:Spire.Presentation.IVideo.Fill" />.
            Note: can return null for certain types of shapes which don't have fill properties.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Fill,self.Ptr)
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
        GetDllLibPpt().IVideo_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().IVideo_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_Click,self.Ptr, value.Ptr)

    @property

    def MouseOver(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse over.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_MouseOver.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_MouseOver.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_MouseOver,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @MouseOver.setter
    def MouseOver(self, value:'ClickHyperlink'):
        GetDllLibPpt().IVideo_set_MouseOver.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_set_MouseOver,self.Ptr, value.Ptr)

    @property
    def IsHidden(self)->bool:
        """
    <summary>
        Indicates whether the shape is hidden.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_IsHidden.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_IsHidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IVideo_get_IsHidden,self.Ptr)
        return ret

    @IsHidden.setter
    def IsHidden(self, value:bool):
        GetDllLibPpt().IVideo_set_IsHidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IVideo_set_IsHidden,self.Ptr, value)

    @property

    def Parent(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Parent,self.Ptr)
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
        GetDllLibPpt().IVideo_get_ZOrderPosition.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_ZOrderPosition.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IVideo_get_ZOrderPosition,self.Ptr)
        return ret

    @ZOrderPosition.setter
    def ZOrderPosition(self, value:int):
        GetDllLibPpt().IVideo_set_ZOrderPosition.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().IVideo_set_ZOrderPosition,self.Ptr, value)

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
        GetDllLibPpt().IVideo_get_Rotation.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Rotation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Rotation,self.Ptr)
        return ret

    @Rotation.setter
    def Rotation(self, value:float):
        GetDllLibPpt().IVideo_set_Rotation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Rotation,self.Ptr, value)

    @property
    def Left(self)->float:
        """
    <summary>
        Gets or sets the x-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().IVideo_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """
    <summary>
        Gets or sets the y-coordinate of the upper-left corner of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().IVideo_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Top,self.Ptr, value)

    @property
    def Width(self)->float:
        """
    <summary>
        Gets or sets the width of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().IVideo_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Gets or sets the height of the shape.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().IVideo_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().IVideo_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().IVideo_set_Height,self.Ptr, value)

    @property

    def AlternativeText(self)->str:
        """
    <summary>
        Gets or sets the alternative text associated with a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_AlternativeText.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_AlternativeText.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IVideo_get_AlternativeText,self.Ptr))
        return ret


    @AlternativeText.setter
    def AlternativeText(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IVideo_set_AlternativeText.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IVideo_set_AlternativeText,self.Ptr,valuePtr)

    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the name of a shape.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IVideo_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IVideo_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IVideo_set_Name,self.Ptr,valuePtr)

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide of a shape.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().IVideo_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().IVideo_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IVideo_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IVideo_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    def RemovePlaceholder(self):
        """
    <summary>
        Removes placeholder from the shape.
    </summary>
        """
        GetDllLibPpt().IVideo_RemovePlaceholder.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_RemovePlaceholder,self.Ptr)

    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().IVideo_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().IVideo_Dispose,self.Ptr)

