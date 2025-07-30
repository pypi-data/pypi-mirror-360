import sys
from ctypes import *
from spire.presentation.common import *
from spire.presentation.common import GetDllLibPpt

from spire.presentation.common.Common import IntPtrArray
from spire.presentation.common.Common import IntPtrWithTypeName
from spire.presentation.common.Common import GetObjVectorFromArray
from spire.presentation.common.Common import GetVectorFromArray
from spire.presentation.common.Common import GetIntPtrArray
from spire.presentation.common.Common import GetByteArray
from spire.presentation.common.Common import GetIntValue
from spire.presentation.common.Common import GetObjIntPtr
from spire.presentation.common.Common import GetStringPtrArray


from spire.presentation.common.SpireObject import SpireObject
from spire.presentation.common.CultureInfo import CultureInfo
from spire.presentation.common.Boolean import Boolean
from spire.presentation.common.Byte import Byte
from spire.presentation.common.Char import Char
from spire.presentation.common.Int16 import Int16
from spire.presentation.common.Int32 import Int32
from spire.presentation.common.Int64 import Int64
from spire.presentation.common.PixelFormat import PixelFormat
from spire.presentation.common.Size import Size
from spire.presentation.common.SizeF import SizeF
from spire.presentation.common.Point import Point
from spire.presentation.common.PointF import PointF
from spire.presentation.common.Rectangle import Rectangle
from spire.presentation.common.RectangleF import RectangleF
from spire.presentation.common.Single import Single
from spire.presentation.common.TimeSpan import TimeSpan
from spire.presentation.common.UInt16 import UInt16
from spire.presentation.common.UInt32 import UInt32
from spire.presentation.common.UInt64 import UInt64
#from spire.presentation.common.ImageFormat import ImageFormat
from spire.presentation.common.Stream import Stream
#from spire.presentation.common.License import License
from spire.presentation.common.Color import Color
#from spire.presentation.common.Image import Image
#from spire.presentation.common.Bitmap import Bitmap
from spire.presentation.common.DateTime import DateTime
from spire.presentation.common.Double import Double
from spire.presentation.common.EmfType import EmfType
from spire.presentation.common.Encoding import Encoding
from spire.presentation.common.FontStyle import FontStyle
#from spire.presentation.common.Font import Font
from spire.presentation.common.GraphicsUnit import GraphicsUnit
from spire.presentation.common.ICollection import ICollection
from spire.presentation.common.IDictionary import IDictionary
from spire.presentation.common.IEnumerable import IEnumerable
from spire.presentation.common.IEnumerator import IEnumerator
from spire.presentation.common.IList import IList
from spire.presentation.common.String import String

from spire.presentation.LicenseProvider import LicenseProvider

from spire.presentation.PptObject import PptObject
from spire.presentation.TextFont import TextFont
from spire.presentation.PdfConformanceLevel import PdfConformanceLevel
from spire.presentation.AudioPlayMode import AudioPlayMode
from spire.presentation.AudioVolumeType import AudioVolumeType
from spire.presentation.TextBulletType import TextBulletType
from spire.presentation.PresetCameraType import PresetCameraType
from spire.presentation.TableBorderType import TableBorderType
from spire.presentation.FontAlignmentType import FontAlignmentType
from spire.presentation.FontCollectionIndex import FontCollectionIndex
from spire.presentation.HyperlinkActionType import HyperlinkActionType
from spire.presentation.LightingDirectionType import LightingDirectionType
from spire.presentation.PresetLightRigType import PresetLightRigType
from spire.presentation.LineEndLength import LineEndLength
from spire.presentation.LineEndType import LineEndType
from spire.presentation.LineEndWidth import LineEndWidth
from spire.presentation.LineCapStyle import LineCapStyle
from spire.presentation.LineDashStyleType import LineDashStyleType
from spire.presentation.LineJoinType import LineJoinType
from spire.presentation.TextLineStyle import TextLineStyle
from spire.presentation.PresetMaterialType import PresetMaterialType
from spire.presentation.TriState import TriState
from spire.presentation.NumberedBulletStyle import NumberedBulletStyle
from spire.presentation.Direction import Direction
from spire.presentation.PlaceholderSize import PlaceholderSize
from spire.presentation.PlaceholderType import PlaceholderType
from spire.presentation.KnownColors import KnownColors
from spire.presentation.PresetShadowValue import PresetShadowValue
from spire.presentation.RectangleAlignment import RectangleAlignment
from spire.presentation.ShapeElementFillSource import ShapeElementFillSource
from spire.presentation.ShapeElementStrokeSource import ShapeElementStrokeSource
from spire.presentation.ShapeType import ShapeType
from spire.presentation.SlideLayoutType import SlideLayoutType
from spire.presentation.SlideOrienation import SlideOrienation
from spire.presentation.SlideSizeType import SlideSizeType
from spire.presentation.ImportDataFormat import ImportDataFormat
from spire.presentation.SystemColorType import SystemColorType
from spire.presentation.TabAlignmentType import TabAlignmentType
from spire.presentation.TableStylePreset import TableStylePreset
from spire.presentation.TextAlignmentType import TextAlignmentType
from spire.presentation.TextAnchorType import TextAnchorType
from spire.presentation.TextAutofitType import TextAutofitType
from spire.presentation.TextCapType import TextCapType
from spire.presentation.TextHorizontalOverflowType import TextHorizontalOverflowType
from spire.presentation.TextShapeType import TextShapeType
from spire.presentation.TextStrikethroughType import TextStrikethroughType
from spire.presentation.TextUnderlineType import TextUnderlineType
from spire.presentation.TextVerticalOverflowType import TextVerticalOverflowType
from spire.presentation.VerticalTextType import VerticalTextType
from spire.presentation.TileFlipMode import TileFlipMode
from spire.presentation.VideoPlayMode import VideoPlayMode
from spire.presentation.ShapeAlignment import ShapeAlignment
from spire.presentation.ShapeArrange import ShapeArrange
from spire.presentation.MetaCharacterType import MetaCharacterType
from spire.presentation.FileFormat import FileFormat
from spire.presentation.SlideShowType import SlideShowType
from spire.presentation.Order import Order
from spire.presentation.PageSlideCount import PageSlideCount
from spire.presentation.FormatAndVersion import FormatAndVersion
from spire.presentation.AnimationRepeatType import AnimationRepeatType
from spire.presentation.BackgroundType import BackgroundType
from spire.presentation.BevelColorType import BevelColorType
from spire.presentation.BevelPresetType import BevelPresetType
from spire.presentation.BlackWhiteMode import BlackWhiteMode
from spire.presentation.BlendMode import BlendMode
from spire.presentation.ColorSchemeIndex import ColorSchemeIndex
from spire.presentation.ColorType import ColorType
from spire.presentation.FillFormatType import FillFormatType
from spire.presentation.GradientShapeType import GradientShapeType
from spire.presentation.GradientStyle import GradientStyle
from spire.presentation.FilterEffectsType import FilterEffectsType
from spire.presentation.PatternFillType import PatternFillType
from spire.presentation.PenAlignmentType import PenAlignmentType
from spire.presentation.PictureFillType import PictureFillType
from spire.presentation.SchemeColor import SchemeColor
from spire.presentation.AnimateType import AnimateType
from spire.presentation.TransitionCornerDirection import TransitionCornerDirection
from spire.presentation.TransitionDirection import TransitionDirection
from spire.presentation.TransitionEightDirection import TransitionEightDirection
from spire.presentation.TransitionInOutDirection import TransitionInOutDirection
from spire.presentation.TransitionSideDirectionType import TransitionSideDirectionType
from spire.presentation.GlitterTransitionDirection import GlitterTransitionDirection
from spire.presentation.TransitionTwoDirection import TransitionTwoDirection
from spire.presentation.TransitionShredInOutDirection import TransitionShredInOutDirection
from spire.presentation.TransitionFlythroughInOutDirection import TransitionFlythroughInOutDirection
from spire.presentation.TransitionRevealLRDirection import TransitionRevealLRDirection
from spire.presentation.TransitionSplitDirection import TransitionSplitDirection
from spire.presentation.TransitionSoundMode import TransitionSoundMode
from spire.presentation.TransitionSpeed import TransitionSpeed
from spire.presentation.TransitionType import TransitionType
from spire.presentation.BehaviorAccumulateType import BehaviorAccumulateType
from spire.presentation.BehaviorAdditiveType import BehaviorAdditiveType
from spire.presentation.ParagraphBuildType import ParagraphBuildType
from spire.presentation.GraphicBuildType import GraphicBuildType
from spire.presentation.AnimationColorDirection import AnimationColorDirection
from spire.presentation.AnimationColorspace import AnimationColorspace
from spire.presentation.AnimationCommandType import AnimationCommandType
from spire.presentation.EffectFillType import EffectFillType
from spire.presentation.TimeNodePresetClassType import TimeNodePresetClassType
from spire.presentation.AnimationRestartType import AnimationRestartType
from spire.presentation.AnimationEffectSubtype import AnimationEffectSubtype
from spire.presentation.AnimationTriggerType import AnimationTriggerType
from spire.presentation.FilterRevealType import FilterRevealType
from spire.presentation.FilterEffectSubtype import FilterEffectSubtype
from spire.presentation.FilterEffectType import FilterEffectType
from spire.presentation.MotionCommandPathType import MotionCommandPathType
from spire.presentation.AnimationMotionOrigin import AnimationMotionOrigin
from spire.presentation.AnimationMotionPathEditMode import AnimationMotionPathEditMode
from spire.presentation.MotionPathPointsType import MotionPathPointsType
from spire.presentation.AnimationCalculationMode import AnimationCalculationMode
from spire.presentation.PropertyValueType import PropertyValueType
from spire.presentation.AnimationEffectType import AnimationEffectType
from spire.presentation.SmartArtColorType import SmartArtColorType
from spire.presentation.SmartArtLayoutType import SmartArtLayoutType
from spire.presentation.SmartArtStyleType import SmartArtStyleType
from spire.presentation.HeaderType import HeaderType
from spire.presentation.AxisPositionType import AxisPositionType
from spire.presentation.AxisType import AxisType
from spire.presentation.ChartBaseUnitType import ChartBaseUnitType
from spire.presentation.ChartDisplayUnitType import ChartDisplayUnitType
from spire.presentation.ChartMarkerType import ChartMarkerType
from spire.presentation.ChartShapeType import ChartShapeType
from spire.presentation.ChartType import ChartType
from spire.presentation.CrossBetweenType import CrossBetweenType
from spire.presentation.ChartCrossesType import ChartCrossesType
from spire.presentation.DataLabelShapeType import DataLabelShapeType
from spire.presentation.DisplayBlanksAsType import DisplayBlanksAsType
from spire.presentation.ErrorBarSimpleType import ErrorBarSimpleType
from spire.presentation.ErrorValueType import ErrorValueType
from spire.presentation.InteriorColorPattern import InteriorColorPattern
from spire.presentation.TreeMapLabelOption import TreeMapLabelOption
from spire.presentation.QuartileCalculation import QuartileCalculation
from spire.presentation.ChartLegendPositionType import ChartLegendPositionType
from spire.presentation.PictureType import PictureType
from spire.presentation.ChartStyle import ChartStyle
from spire.presentation.TickLabelPositionType import TickLabelPositionType
from spire.presentation.TickMarkType import TickMarkType
from spire.presentation.TrendlinesType import TrendlinesType
from spire.presentation.ChartDataLabelPosition import ChartDataLabelPosition
from spire.presentation.EffectNode import EffectNode

from spire.presentation.AudioCD import AudioCD
from spire.presentation.IDigitalSignature import IDigitalSignature
from spire.presentation.IDigitalSignatures import IDigitalSignatures

from spire.presentation.IActivePresentation import IActivePresentation
from spire.presentation.IActiveSlide import IActiveSlide
from spire.presentation.ColorFormat import ColorFormat
from spire.presentation.GradientStop import GradientStop
from spire.presentation.GradientStopData import GradientStopData
from spire.presentation.GradientStopList import GradientStopList
from spire.presentation.GradientStopDataCollection import GradientStopDataCollection
from spire.presentation.GradientStopCollection import GradientStopCollection
from spire.presentation.LinearGradientFill import LinearGradientFill
from spire.presentation.PatternFillFormat import PatternFillFormat
from spire.presentation.GradientFillFormat import GradientFillFormat
from spire.presentation.PictureData import PictureData
from spire.presentation.PictureShape import PictureShape
from spire.presentation.RelativeRectangle import RelativeRectangle
from spire.presentation.PictureFillFormat import PictureFillFormat
from spire.presentation.FillFormat import FillFormat
from spire.presentation.LineFillFormat import LineFillFormat
from spire.presentation.IChartGridLine import IChartGridLine
from spire.presentation.TextLineFormat import TextLineFormat
from spire.presentation.BlendEffect import BlendEffect
from spire.presentation.InnerShadowNode import InnerShadowNode
from spire.presentation.InnerShadowEffect import InnerShadowEffect
from spire.presentation.OuterShadowNode import OuterShadowNode
from spire.presentation.OuterShadowEffect import OuterShadowEffect
from spire.presentation.PresetShadow import PresetShadow
from spire.presentation.PresetShadowNode import PresetShadowNode
from spire.presentation.ReflectionNode import ReflectionNode
from spire.presentation.ReflectionEffect import ReflectionEffect
from spire.presentation.SoftEdgeNode import SoftEdgeNode
from spire.presentation.SoftEdgeEffect import SoftEdgeEffect
from spire.presentation.EffectDag import EffectDag
from spire.presentation.EffectStyle import EffectStyle
from spire.presentation.TextCharacterProperties import TextCharacterProperties
from spire.presentation.DefaultTextRangeProperties import DefaultTextRangeProperties
from spire.presentation.TextRange import TextRange
from spire.presentation.TextRangeList import TextRangeList
from spire.presentation.TextRangeCollection import TextRangeCollection
from spire.presentation.ParagraphProperties import ParagraphProperties
from spire.presentation.TextParagraph import TextParagraph
from spire.presentation.ParagraphList import ParagraphList
from spire.presentation.ParagraphCollection import ParagraphCollection
from spire.presentation.FormatScheme import FormatScheme
from spire.presentation.ShapeBevelStyle import ShapeBevelStyle
from spire.presentation.LightRig import LightRig
from spire.presentation.ShapeThreeD import ShapeThreeD
from spire.presentation.Camera import Camera
from spire.presentation.FormatThreeD import FormatThreeD
from spire.presentation.TextParagraphProperties import TextParagraphProperties
from spire.presentation.TextStyle import TextStyle
from spire.presentation.LineText import LineText
from spire.presentation.ITextFrameProperties import ITextFrameProperties


from spire.presentation.TextHighLightingOptions import TextHighLightingOptions
from spire.presentation.DocumentEditException import DocumentEditException
from spire.presentation.DocumentReadException import DocumentReadException
from spire.presentation.DocumentUnkownFormatException import DocumentUnkownFormatException
#from spire.presentation.PresentationPrintDocument import PresentationPrintDocument
from spire.presentation.IAudioData import IAudioData
from spire.presentation.WavAudioCollection import WavAudioCollection
from spire.presentation.TagList import TagList
from spire.presentation.TagCollection import TagCollection
from spire.presentation.IShape import IShape


from spire.presentation.Comment import Comment
from spire.presentation.CommentList import CommentList
from spire.presentation.CommentCollection import CommentCollection
from spire.presentation.ICommentAuthor import ICommentAuthor
from spire.presentation.InsertPlaceholderType import InsertPlaceholderType
from spire.presentation.ProjectionType import ProjectionType

from spire.presentation.Field import Field
from spire.presentation.FieldType import FieldType



from spire.presentation.AppException import AppException



from spire.presentation.Placeholder import Placeholder
from spire.presentation.ShapeStyle import ShapeStyle
from spire.presentation.ClickHyperlink import ClickHyperlink
from spire.presentation.BaseShapeLocking import BaseShapeLocking
from spire.presentation.GraphicalNodeLocking import GraphicalNodeLocking
from spire.presentation.SimpleShapeBaseLocking import SimpleShapeBaseLocking
from spire.presentation.ShapeLocking import ShapeLocking

from spire.presentation.FillListBase import FillListBase
from spire.presentation.FillStyleList import FillStyleList
from spire.presentation.GraphicFrame import GraphicFrame
from spire.presentation.Shape import Shape

from spire.presentation.IEmbedImage import IEmbedImage
from spire.presentation.ShapeNode import ShapeNode

from spire.presentation.ShapeAdjust import ShapeAdjust
from spire.presentation.ShapeAdjustmentList import ShapeAdjustmentList
from spire.presentation.ShapeAdjustCollection import ShapeAdjustCollection
from spire.presentation.IAutoShape import IAutoShape

from spire.presentation.HistogramAxisFormat import HistogramAxisFormat
from spire.presentation.Geography import Geography
from spire.presentation.IChartEffectFormat import IChartEffectFormat
from spire.presentation.ChartTextArea import ChartTextArea
from spire.presentation.IChartAxis import IChartAxis
from spire.presentation.ChartAxis import ChartAxis
from spire.presentation.CellRange import CellRange
from spire.presentation.CellRanges import CellRanges
from spire.presentation.ChartDataLabel import ChartDataLabel
from spire.presentation.ChartDataLabelCollection import ChartDataLabelCollection

from spire.presentation.ChartData import ChartData
from spire.presentation.ChartEffectFormat import ChartEffectFormat
from spire.presentation.ChartDataPoint import ChartDataPoint
from spire.presentation.ChartDataPointCollection import ChartDataPointCollection

from spire.presentation.IErrorBarsFormat import IErrorBarsFormat
from spire.presentation.ITrendlineLabel import ITrendlineLabel
from spire.presentation.ITrendlines import ITrendlines
from spire.presentation.ChartSeriesDataFormat import ChartSeriesDataFormat
from spire.presentation.ChartSeriesFormatCollection import ChartSeriesFormatCollection
from spire.presentation.ChartCategory import ChartCategory


from spire.presentation.ChartRotationThreeD import ChartRotationThreeD
from spire.presentation.ChartDataTable import ChartDataTable
from spire.presentation.LegendEntry import LegendEntry
from spire.presentation.LegendEntryCollection import LegendEntryCollection

from spire.presentation.ChartLegend import ChartLegend

from spire.presentation.ChartWallsOrFloor import ChartWallsOrFloor
from spire.presentation.ChartPlotArea import ChartPlotArea


from spire.presentation.ChartCategoryCollection import ChartCategoryCollection

from spire.presentation.IChart import IChart
from spire.presentation.SlidePictureLocking import SlidePictureLocking
from spire.presentation.IAudio import IAudio
from spire.presentation.SlidePicture import SlidePicture
from spire.presentation.Cell import Cell
from spire.presentation.CellCollection import CellCollection
from spire.presentation.TableRow import TableRow
from spire.presentation.RowList import RowList
from spire.presentation.TableRowCollection import TableRowCollection
from spire.presentation.TableColumn import TableColumn
from spire.presentation.ColumnList import ColumnList
from spire.presentation.ColumnCollection import ColumnCollection

from spire.presentation.ITable import ITable
from spire.presentation.VideoData import VideoData
from spire.presentation.IVideo import IVideo

from spire.presentation.IOleObject import IOleObject
from spire.presentation.ISmartArtNode import ISmartArtNode
from spire.presentation.ISmartArtNodeCollection import ISmartArtNodeCollection
from spire.presentation.ISmartArt import ISmartArt
from spire.presentation.GroupShape import GroupShape

from spire.presentation.ShapeList import ShapeList
from spire.presentation.TabData import TabData
from spire.presentation.ColorScheme import ColorScheme
from spire.presentation.SlideColorScheme import SlideColorScheme
from spire.presentation.FontScheme import FontScheme
from spire.presentation.Theme import Theme
from spire.presentation.SlideBackground import SlideBackground
from spire.presentation.ShapeCollection import ShapeCollection
from spire.presentation.ActiveSlide import ActiveSlide


from spire.presentation.ConnectorLocking import ConnectorLocking

from spire.presentation.LocaleFonts import LocaleFonts


from spire.presentation.GroupShapeLocking import GroupShapeLocking

from spire.presentation.OleObjectProperties import OleObjectProperties
from spire.presentation.OleObject import OleObject

from spire.presentation.ILayout import ILayout





from spire.presentation.SaveToPdfOption import SaveToPdfOption
from spire.presentation.SaveToHtmlOption import SaveToHtmlOption
from spire.presentation.SaveToPptxOption import SaveToPptxOption
from spire.presentation.IDocumentProperty import IDocumentProperty

from spire.presentation.TimeNode import TimeNode
from spire.presentation.TimeNodeMedia import TimeNodeMedia
from spire.presentation.TimeNodeAudio import TimeNodeAudio
from spire.presentation.TimeNodes import TimeNodes
from spire.presentation.Transition import Transition
from spire.presentation.CoverSlideTransition import CoverSlideTransition
from spire.presentation.ZoomSlideTransition import ZoomSlideTransition
from spire.presentation.OptionalBlackTransition import OptionalBlackTransition
from spire.presentation.BlindsSlideTransition import BlindsSlideTransition
from spire.presentation.SideDirectionTransition import SideDirectionTransition
from spire.presentation.GlitterTransition import GlitterTransition
from spire.presentation.LRTransition import LRTransition
from spire.presentation.ShredTransition import ShredTransition
from spire.presentation.FlythroughTransition import FlythroughTransition
from spire.presentation.RevealTransition import RevealTransition
from spire.presentation.InvXTransition import InvXTransition
from spire.presentation.SplitSlideTransition import SplitSlideTransition
from spire.presentation.StripsSlideTransition import StripsSlideTransition
from spire.presentation.WheelSlideTransition import WheelSlideTransition
from spire.presentation.SlideShowTransition import SlideShowTransition
from spire.presentation.GraphicAnimation import GraphicAnimation
from spire.presentation.Timing import Timing
from spire.presentation.CommonBehavior import CommonBehavior
from spire.presentation.AnimationColorBehavior import AnimationColorBehavior
from spire.presentation.AnimationColorTransform import AnimationColorTransform
from spire.presentation.AnimationCommandBehavior import AnimationCommandBehavior
from spire.presentation.TextAnimation import TextAnimation
from spire.presentation.AnimationEffect import AnimationEffect
from spire.presentation.AnimationFilterEffect import AnimationFilterEffect
from spire.presentation.MotionCmdPath import MotionCmdPath
from spire.presentation.AnimationMotion import AnimationMotion
from spire.presentation.MotionPath import MotionPath
from spire.presentation.TimeAnimationValue import TimeAnimationValue
from spire.presentation.TimeAnimationValueCollection import TimeAnimationValueCollection
from spire.presentation.AnimationProperty import AnimationProperty
from spire.presentation.AnimationRotation import AnimationRotation
from spire.presentation.AnimationScale import AnimationScale
from spire.presentation.AnimationEffectCollection import AnimationEffectCollection
from spire.presentation.SequenceCollection import SequenceCollection
from spire.presentation.AnimationSet import AnimationSet



from spire.presentation.TextAnimationCollection import TextAnimationCollection
from spire.presentation.TimeLine import TimeLine

from spire.presentation.IMasterLayouts import IMasterLayouts
from spire.presentation.NotesSlide import NotesSlide
from spire.presentation.INoteMasterSlide import INoteMasterSlide
from spire.presentation.IMasterSlide import IMasterSlide
from spire.presentation.OleObjectCollection import OleObjectCollection
from spire.presentation.ISlide import ISlide
from spire.presentation.SlideList import SlideList
from spire.presentation.SlideSize import SlideSize
from spire.presentation.TabStop import TabStop
from spire.presentation.Section import Section
from spire.presentation.SectionList import SectionList


from spire.presentation.MasterTheme import MasterTheme

from spire.presentation._Presentation import _Presentation
from spire.presentation.SlideCollection import SlideCollection
from spire.presentation.VideoCollection import VideoCollection
from spire.presentation.IImageData import IImageData
from spire.presentation.EmbedImageList import EmbedImageList
from spire.presentation.ImageCollection import ImageCollection
from spire.presentation.MasterSlideList import MasterSlideList
from spire.presentation.MasterSlideCollection import MasterSlideCollection

from spire.presentation.CommentAuthorList import CommentAuthorList
from spire.presentation.CommentAuthorCollection import CommentAuthorCollection


from spire.presentation.Presentation import Presentation

from spire.presentation.Backdrop import Backdrop




from spire.presentation.ExtensionList import ExtensionList






from spire.presentation.ImageTransformBase import ImageTransformBase

from spire.presentation.BlurNode import BlurNode
from spire.presentation.FillOverlayEffect import FillOverlayEffect
from spire.presentation.GlowNode import GlowNode
from spire.presentation.GlowEffect import GlowEffect
from spire.presentation.ImageTransform import ImageTransform


from spire.presentation.PresentationTranslator import PresentationTranslator

from spire.presentation.CommonBehaviorCollection import CommonBehaviorCollection
from spire.presentation.EffectStyleList import EffectStyleList
from spire.presentation.EffectStyleCollection import EffectStyleCollection

from spire.presentation.FillStyleCollection import FillStyleCollection
from spire.presentation.FillFormatList import FillFormatList
from spire.presentation.FillFormatCollection import FillFormatCollection



from spire.presentation.TextLineFormatList import TextLineFormatList
from spire.presentation.TextLineFormatCollection import TextLineFormatCollection
from spire.presentation.LineStyleList import LineStyleList
from spire.presentation.LineStyleCollection import LineStyleCollection





from spire.presentation.TabStopList import TabStopList
from spire.presentation.TabStopCollection import TabStopCollection

from spire.presentation.GraphicAnimationCollection import GraphicAnimationCollection






from spire.presentation.EffectDataCollection import EffectDataCollection
from spire.presentation.ImageTransformEffectCollection import ImageTransformEffectCollection
from spire.presentation.SlideColorSchemeCollection import SlideColorSchemeCollection

from spire.presentation.LayoutProperty import LayoutProperty






