from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ISmartArtNode (SpireObject) :
    """

    """
    @property

    def ChildNodes(self)->'ISmartArtNodeCollection':
        from spire.presentation.ISmartArtNodeCollection import ISmartArtNodeCollection
        GetDllLibPpt().ISmartArtNode_get_ChildNodes.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_ChildNodes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_ChildNodes,self.Ptr)
        ret = None if intPtr==None else ISmartArtNodeCollection(intPtr)
        return ret


    @property

    def TextFrame(self)->'ITextFrameProperties':
        """

        """
        GetDllLibPpt().ISmartArtNode_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @TextFrame.setter
    def TextFrame(self, value:'ITextFrameProperties'):
        GetDllLibPpt().ISmartArtNode_set_TextFrame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_TextFrame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
    <summary>
        Gets the LineFormat object that contains line formatting properties for a SmartArtNode.
            Read-only <see cref="P:Spire.Presentation.Diagrams.ISmartArtNode.Line" />.
    </summary>
        """
        GetDllLibPpt().ISmartArtNode_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def LinkLine(self)->'TextLineFormat':
        """

        """
        GetDllLibPpt().ISmartArtNode_get_LinkLine.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_LinkLine.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_LinkLine,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property
    def CustomText(self)->bool:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_CustomText.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_CustomText.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_CustomText,self.Ptr)
        return ret

    @CustomText.setter
    def CustomText(self, value:bool):
        GetDllLibPpt().ISmartArtNode_set_CustomText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_CustomText,self.Ptr, value)

    @property
    def IsAssistant(self)->bool:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_IsAssistant.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_IsAssistant.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_IsAssistant,self.Ptr)
        return ret

    @IsAssistant.setter
    def IsAssistant(self, value:bool):
        GetDllLibPpt().ISmartArtNode_set_IsAssistant.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_IsAssistant,self.Ptr, value)

    @property
    def Level(self)->int:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_Level.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Level.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Level,self.Ptr)
        return ret

    @property
    def Position(self)->int:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Position,self.Ptr)
        return ret

    @Position.setter
    def Position(self, value:int):
        GetDllLibPpt().ISmartArtNode_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_Position,self.Ptr, value)

    @property

    def Click(self)->'ClickHyperlink':
        """
    <summary>
        Gets or sets the hyperlink defined for mouse click.
            Read/write <see cref="T:Spire.Presentation.ClickHyperlink" />.
    </summary>
        """
        GetDllLibPpt().ISmartArtNode_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        GetDllLibPpt().ISmartArtNode_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_Click,self.Ptr, value.Ptr)

    @property
    def NodeHeight(self)->int:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_NodeHeight.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeHeight.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeHeight,self.Ptr)
        return ret

    @NodeHeight.setter
    def NodeHeight(self, value:int):
        GetDllLibPpt().ISmartArtNode_set_NodeHeight.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeHeight,self.Ptr, value)

    @property
    def NodeWidth(self)->int:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_NodeWidth.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeWidth,self.Ptr)
        return ret

    @NodeWidth.setter
    def NodeWidth(self, value:int):
        GetDllLibPpt().ISmartArtNode_set_NodeWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeWidth,self.Ptr, value)

    @property
    def NodeX(self)->int:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_NodeX.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeX.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeX,self.Ptr)
        return ret

    @NodeX.setter
    def NodeX(self, value:int):
        GetDllLibPpt().ISmartArtNode_set_NodeX.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeX,self.Ptr, value)

    @property
    def NodeY(self)->int:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_NodeY.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeY.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeY,self.Ptr)
        return ret

    @NodeY.setter
    def NodeY(self, value:int):
        GetDllLibPpt().ISmartArtNode_set_NodeY.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeY,self.Ptr, value)

    @property
    def TrChanged(self)->bool:
        """

        """
        GetDllLibPpt().ISmartArtNode_get_TrChanged.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_TrChanged.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_TrChanged,self.Ptr)
        return ret

    @TrChanged.setter
    def TrChanged(self, value:bool):
        GetDllLibPpt().ISmartArtNode_set_TrChanged.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_TrChanged,self.Ptr, value)

    @property

    def FillFormat(self)->'FillFormat':
        """

        """
        GetDllLibPpt().ISmartArtNode_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @FillFormat.setter
    def FillFormat(self, value:'FillFormat'):
        GetDllLibPpt().ISmartArtNode_set_FillFormat.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_FillFormat,self.Ptr, value.Ptr)

