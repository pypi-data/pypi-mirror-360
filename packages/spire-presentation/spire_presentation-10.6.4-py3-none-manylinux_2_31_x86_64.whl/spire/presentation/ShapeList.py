from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple

from plum.dispatcher import Dispatcher
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeList (SpireObject) :
   
    @dispatch
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().ShapeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ShapeList_get_Item.restype=IntPtrWithTypeName
        intPtrWithType = CallCFunction(GetDllLibPpt().ShapeList_get_Item,self.Ptr, key)
        ret = None if intPtrWithType==None else self._create(intPtrWithType)
        return ret

    @staticmethod
    def _create(intPtrWithTypeName:IntPtrWithTypeName)->'IShape':
        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'GroupShape'):
            ret = GroupShape(intPtr)
        elif (strName == 'IChart'):
            ret = IChart(intPtr)
        elif (strName == 'IAudio'):
            ret = IAudio(intPtr)
        elif (strName == 'IAutoShape'):
            ret = IAutoShape(intPtr)
        elif (strName == 'IEmbedImage'):
            ret = SlidePicture(intPtr)
        elif (strName == 'ITable'):
            ret = ITable(intPtr)
        elif (strName == 'IVideo'):
            ret = IVideo(intPtr)
        elif (strName == 'IOleObject'):
            ret = IOleObject(intPtr)
        elif (strName == 'ISmartArt'):
            ret = ISmartArt(intPtr)
        elif (strName == 'ShapeNode'):
            ret = ShapeNode(intPtr)
        else:
            ret = IShape(intPtr)

        return ret

    """
    <summary>
        Represents a collection of a shapes.
    </summary>
    """

    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().ShapeList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ShapeList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
    <summary>
        Gets parent object for a Shapes collection.
            Read-only <see cref="T:System.Object" />. See also <see cref="T:Spire.Presentation.IActivePresentation" />.
    </summary>
        """
        GetDllLibPpt().ShapeList_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().ShapeList_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def AddFromHtml(self ,htmlText:str):
        """
    <summary>
        Adds text from specified html string.
    </summary>
    <param name="htmlText">HTML text.</param>
        """
        
        htmlTextPtr = StrToPtr(htmlText)
        GetDllLibPpt().ShapeList_AddFromHtml.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().ShapeList_AddFromHtml,self.Ptr,htmlTextPtr)

    def AddFromSVG(self ,svgFilePath:str,rectangle:'RectangleF'):
        """
    
        """
        
        svgFilePathPtr = StrToPtr(svgFilePath)
        intPtrrectangle:c_void_p = rectangle.Ptr
        GetDllLibPpt().ShapeList_AddFromSVG.argtypes=[c_void_p ,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_AddFromSVG,self.Ptr,svgFilePathPtr,intPtrrectangle)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeList_Equals,self.Ptr, intPtrobj)
        return ret

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ShapeList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ShapeList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'IShape':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.Shape" />.
    </summary>
        """
        
        GetDllLibPpt().ShapeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ShapeList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IShape(intPtr)
        return ret

    def SaveAsImage(self ,shapeIndex:int, dpiX:int = 96,dpiY:int=96)->'Stream':
        """
    <summary>
        Save shapes to Image.
    </summary>
    <param name="shapeIndex">Represents the shape index in the indicated slide's shapes collection</param>
    <returns></returns>
        """
        GetDllLibPpt().ShapeList_SaveAsImageDpi.argtypes=[c_void_p ,c_int,c_int,c_int]
        GetDllLibPpt().ShapeList_SaveAsImageDpi.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_SaveAsImageDpi,self.Ptr, shapeIndex,dpiX,dpiY)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveAsEMF(self ,shapeIndex:int,filePath:str):
        """
    <summary>
        Save shapes to EMF.
    </summary>
    <param name="shapeIndex">Represents the shape index in the indicated slide's shapes collection</param>
    <param name="filePahth">Represents the save path</param>
    <returns></returns>
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_SaveAsEMF.argtypes=[c_void_p ,c_int,c_char_p]
        CallCFunction(GetDllLibPpt().ShapeList_SaveAsEMF,self.Ptr, shapeIndex,filePathPtr)


    def CreateChart(self ,baseChart:'IChart',rectangle:'RectangleF',nIndex:int)->'IChart':
        """
    <summary>
        clone basechart and insert into shapes
    </summary>
    <param name="baseChart">source chart</param>
    <param name="rectangle">Rectangle should be inserted</param>
    <param name="nIndex">index should be inserted.-1 mean append at the last.</param>
    <returns></returns>
        """
        intPtrbaseChart:c_void_p = baseChart.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_CreateChart.argtypes=[c_void_p ,c_void_p,c_void_p,c_int]
        GetDllLibPpt().ShapeList_CreateChart.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_CreateChart,self.Ptr, intPtrbaseChart,intPtrrectangle,nIndex)
        ret = None if intPtr==None else IChart(intPtr)
        return ret

    
    def AppendChartInit(self ,type:ChartType,rectangle:RectangleF,init:bool)->'IChart':
        """
    <summary>
        Adds a new chart.
    </summary>
    <param name="type">Chart type</param>
    <param name="rectangle">rectangle should be inserted.</param>
    <param name="init">init chart use default data .</param>
    <returns></returns>
        """
        enumtype:c_int = type.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendChart.argtypes=[c_void_p ,c_int,c_void_p,c_bool]
        GetDllLibPpt().ShapeList_AppendChart.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendChart,self.Ptr, enumtype,intPtrrectangle,init)
        ret = None if intPtr==None else IChart(intPtr)
        return ret

    def AppendChart(self ,type:ChartType,rectangle:RectangleF)->'IChart':
        """
    <summary>
        Adds a new chart.init chart use default data
    </summary>
    <param name="type">Chart type</param>
    <param name="rectangle">rectangle should be inserted.</param>
    <returns></returns>
        """
        enumtype:c_int = type.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendChartTR.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().ShapeList_AppendChartTR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendChartTR,self.Ptr, enumtype,intPtrrectangle)
        ret = None if intPtr==None else IChart(intPtr)
        return ret



    def AppendSmartArt(self ,x:float,y:float,width:float,height:float,layoutType:'SmartArtLayoutType')->'ISmartArt':
        """

        """
        enumlayoutType:c_int = layoutType.value

        GetDllLibPpt().ShapeList_AppendSmartArt.argtypes=[c_void_p ,c_float,c_float,c_float,c_float,c_int]
        GetDllLibPpt().ShapeList_AppendSmartArt.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendSmartArt,self.Ptr, x,y,width,height,enumlayoutType)
        ret = None if intPtr==None else ISmartArt(intPtr)
        return ret



    def InsertChart(self ,index:int,type:'ChartType',rectangle:'RectangleF',init:bool):
        """
    <summary>
        Add a new chart to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="type">Chart type</param>
    <param name="rectangle">Rectangle should inserted.</param>
        """
        enumtype:c_int = type.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertChart.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_bool]
        CallCFunction(GetDllLibPpt().ShapeList_InsertChart,self.Ptr, index,enumtype,intPtrrectangle,init)

    def AppendOleObject(self ,objectName:str,objectData:'Stream',rectangle:RectangleF)->IOleObject:
        """
    <summary>
        Add a new OleObject to Collection
    </summary>
    <param name="objectName">Object Name</param>
    <param name="objectData">Object Data</param>
    <param name="rectangle">Rectangle should be inserted.</param>
    <returns></returns>
        """
        intPtrobjectData:c_void_p = objectData.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        objectNamePtr = StrToPtr(objectName)
        GetDllLibPpt().ShapeList_AppendOleObject.argtypes=[c_void_p ,c_char_p,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendOleObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendOleObject,self.Ptr,objectNamePtr,intPtrobjectData,intPtrrectangle)
        ret = None if intPtr==None else IOleObject(intPtr)
        return ret
#


#    @dispatch
#
#    def AppendOleObject(self ,objectName:str,objectData:'Byte[]',rectangle:RectangleF)->IOleObject:
#        """
#    <summary>
#        Add a new OleObject to Collection
#    </summary>
#    <param name="objectName">Object Name</param>
#    <param name="objectData">Object Data</param>
#    <param name="rectangle">Rectangle should be inserted.</param>
#    <returns></returns>
#        """
#        #arrayobjectData:ArrayTypeobjectData = ""
#        countobjectData = len(objectData)
#        ArrayTypeobjectData = c_void_p * countobjectData
#        arrayobjectData = ArrayTypeobjectData()
#        for i in range(0, countobjectData):
#            arrayobjectData[i] = objectData[i].Ptr
#
#        intPtrrectangle:c_void_p = rectangle.Ptr
#
#        GetDllLibPpt().ShapeList_AppendOleObjectOOR.argtypes=[c_void_p ,c_wchar_p,ArrayTypeobjectData,c_void_p]
#        GetDllLibPpt().ShapeList_AppendOleObjectOOR.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendOleObjectOOR,self.Ptr, objectName,arrayobjectData,intPtrrectangle)
#        ret = None if intPtr==None else IOleObject(intPtr)
#        return ret
#


    def InsertOleObject(self ,index:int,objectName:str,objectData:'Stream',rectangle:RectangleF):
        """
    <summary>
        Insert a object to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="objectName">Object name</param>
    <param name="objectData">Object data</param>
    <param name="rectangle">Rectangle should be inserted</param>
        """
        intPtrobjectData:c_void_p = objectData.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        objectNamePtr = StrToPtr(objectName)
        GetDllLibPpt().ShapeList_InsertOleObject.argtypes=[c_void_p ,c_int,c_char_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertOleObject,self.Ptr, index,objectNamePtr,intPtrobjectData,intPtrrectangle)


#    @dispatch
#
#    def InsertOleObject(self ,index:int,objectName:str,objectData:'Byte[]',rectangle:RectangleF):
#        """
#    <summary>
#        Insert a object to collection.
#    </summary>
#    <param name="index">Index should be inserted.</param>
#    <param name="objectName">Object name</param>
#    <param name="objectData">Object data</param>
#    <param name="rectangle">Rectangle should be inserted</param>
#        """
#        #arrayobjectData:ArrayTypeobjectData = ""
#        countobjectData = len(objectData)
#        ArrayTypeobjectData = c_void_p * countobjectData
#        arrayobjectData = ArrayTypeobjectData()
#        for i in range(0, countobjectData):
#            arrayobjectData[i] = objectData[i].Ptr
#
#        intPtrrectangle:c_void_p = rectangle.Ptr
#
#        GetDllLibPpt().ShapeList_InsertOleObjectIOOR.argtypes=[c_void_p ,c_int,c_wchar_p,ArrayTypeobjectData,c_void_p]
#        CallCFunction(GetDllLibPpt().ShapeList_InsertOleObjectIOOR,self.Ptr, index,objectName,arrayobjectData,intPtrrectangle)

   
    def AppendVideoMedia(self ,filePath:str,rectangle:RectangleF)->'IVideo':
        """
    <summary>
        Add a new video to collection. innerLink mode
    </summary>
    <param name="filePath"></param>
    <param name="rectangle"></param>
    <returns></returns>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendVideoMedia.argtypes=[c_void_p ,c_char_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendVideoMedia.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendVideoMedia,self.Ptr,filePathPtr,intPtrrectangle)
        ret = None if intPtr==None else IVideo(intPtr)
        return ret
    
    def AppendVideoMediaLink(self ,filePath:str,rectangle:RectangleF,isInnerLink:bool)->'IVideo':
        """
    <summary>
        Add a new video to collection.
    </summary>
    <param name="filePath"></param>
    <param name="rectangle"></param>
    <param name="isInnerLink"></param>
    <returns></returns>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendVideoMediaFRI.argtypes=[c_void_p ,c_char_p,c_void_p,c_bool]
        GetDllLibPpt().ShapeList_AppendVideoMediaFRI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendVideoMediaFRI,self.Ptr,filePathPtr,intPtrrectangle,isInnerLink)
        ret = None if intPtr==None else IVideo(intPtr)
        return ret


    def AppendVideoMediaByStream(self ,stream:Stream,rectangle:RectangleF)->'IVideo':
        """
    <summary>
        Add a new video to collection by stream.
    </summary>
    <param name="stream">video stream object</param>
    <param name="rectangle">rectangle for placing video</param>
    <param name="isInnerLink"></param>
    <returns></returns>
        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendVideoMediaSR.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendVideoMediaSR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendVideoMediaSR,self.Ptr, intPtrstream,intPtrrectangle)
        ret = None if intPtr==None else IVideo(intPtr)
        return ret



    def InsertVideoMedia(self ,index:int,filePath:str,rectangle:'RectangleF'):
        """
    <summary>
        Adds a new video to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="filePath">Video file path.</param>
    <param name="rectangle">Rectangle should be inserted.</param>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertVideoMedia.argtypes=[c_void_p ,c_int,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertVideoMedia,self.Ptr, index,filePathPtr,intPtrrectangle)

    @dispatch

    def AppendAudioMediaByRect(self ,rectangle:RectangleF)->'IAudio':
        """
    <summary>
        Adds an Audio from CD
    </summary>
    <param name="rectangle">Rectangle should be inserted</param>
    <returns></returns>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendAudioMedia.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeList_AppendAudioMedia.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMedia,self.Ptr, intPtrrectangle)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def InsertAudioMedia(self ,index:int,rectangle:RectangleF):
        """
    <summary>
        Insert an Audio From CD.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="rectangle">Rectangle should be inserted.</param>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertAudioMedia.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMedia,self.Ptr, index,intPtrrectangle)

    @dispatch

    def AppendAudioMediaByPathXYEmbed(self ,filePath:str,X:float,Y:float,isEmbed:bool)->'IAudio':
        """
    <summary>
        Adds a new audio to list.
    </summary>
    <param name="filePath">Audio file name</param>
    <param name="X">X Position</param>
    <param name="Y">Y Position</param>
    <param name="isEmbed">Whether embed or not</param>
    <returns></returns>
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendAudioMediaFXYI.argtypes=[c_void_p ,c_char_p,c_float,c_float,c_bool]
        GetDllLibPpt().ShapeList_AppendAudioMediaFXYI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFXYI,self.Ptr,filePathPtr,X,Y,isEmbed)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def AppendAudioMediaByPathXY(self ,filePath:str,X:float,Y:float)->'IAudio':
        """
    <summary>
        Adds a new audio to list.
    </summary>
    <param name="filePath">Audio file name</param>
    <param name="X">X Position</param>
    <param name="Y">Y Position</param>
    <returns></returns>
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendAudioMediaFXY.argtypes=[c_void_p ,c_char_p,c_float,c_float]
        GetDllLibPpt().ShapeList_AppendAudioMediaFXY.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFXY,self.Ptr,filePathPtr,X,Y)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret



    def AppendAudioMediaEmbed(self ,filePath:str,rectangle:RectangleF,isEmbed:bool)->'IAudio':
        """
    <summary>
        Adds a new audio to list.
    </summary>
    <param name="filePath">Audio file name</param>
    <param name="rectangle">Rectangle should be inserted</param>
    <param name="isEmbed">Whether embed or not,default not</param>
    <returns></returns>
        """
        filePathPtr = StrToPtr(filePath)
        intPtrrectangle:c_void_p = rectangle.Ptr
        GetDllLibPpt().ShapeList_AppendAudioMediaFRI.argtypes=[c_void_p ,c_char_p,c_void_p,c_bool]
        GetDllLibPpt().ShapeList_AppendAudioMediaFRI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFRI,self.Ptr,filePathPtr,intPtrrectangle,isEmbed)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret
    
    def AppendAudioMedia(self ,filePath:str,rectangle:RectangleF)->'IAudio':
        """
    <summary>
        Adds a new audio to list.
    </summary>
    <param name="filePath">Audio file name</param>
    <param name="rectangle">Rectangle should be inserted</param>
    <returns></returns>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendAudioMediaFR.argtypes=[c_void_p ,c_char_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendAudioMediaFR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFR,self.Ptr,filePathPtr,intPtrrectangle)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,rectangle:RectangleF,isEmbed:bool):
        """
    <summary>
        Insert an audio to collection.
    </summary>
    <param name="filePath">Audio file path</param>
    <param name="rectangle">Rectangle should be inserted.</param>
    <param name="isEmbed">Whether embed or not,default not</param>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFRI.argtypes=[c_void_p ,c_int,c_char_p,c_void_p,c_bool]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFRI,self.Ptr, index,filePathPtr,intPtrrectangle,isEmbed)

    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,rectangle:RectangleF):
        """
    <summary>
        Insert an audio to collection.
    </summary>
    <param name="filePath">Audio file path</param>
    <param name="rectangle">Rectangle should be inserted.</param>
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFR.argtypes=[c_void_p ,c_int,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFR,self.Ptr, index,filePathPtr,intPtrrectangle)

    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,X:float,Y:float,isEmbed:bool):
        """
    <summary>
        Insert an audio to collection.
    </summary>
    <param name="filePath">Audio file path</param>
    <param name="X">X Position</param>
    <param name="Y">Y Position</param>
    <param name="isEmbed">Whether embed or not,default not</param>
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFXYI.argtypes=[c_void_p ,c_int,c_char_p,c_float,c_float,c_bool]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFXYI,self.Ptr, index,filePathPtr,X,Y,isEmbed)

    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,X:float,Y:float):
        """
    <summary>
        Insert an audio to collection.
    </summary>
    <param name="filePath">Audio file path</param>
    <param name="X">X Position</param>
    <param name="Y">Y Position</param>
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFXY.argtypes=[c_void_p ,c_int,c_char_p,c_float,c_float]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFXY,self.Ptr, index,filePathPtr,X,Y)


    def AppendAudioMediaByStreamRect(self ,stream:Stream,rectangle:RectangleF)->'IAudio':
        """
    <summary>
        Adds a new audio to list.
    </summary>
    <param name="stream">Audio stream</param>
    <param name="rectangle">Rectangle should be inserted</param>
    <returns></returns>
        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendAudioMediaSR.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendAudioMediaSR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaSR,self.Ptr, intPtrstream,intPtrrectangle)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    def AppendAudioMediaByStreamFloat(self ,stream:Stream,X:float,Y:float)->'IAudio':
        """
    <summary>
        Adds a new audio to list.
    </summary>
    <param name="stream">Audio stream</param>
    <param name="rectangle">Rectangle should be inserted</param>
    <returns></returns>
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().ShapeList_AppendAudioMediaSXY.argtypes=[c_void_p ,c_void_p,c_float,c_float]
        GetDllLibPpt().ShapeList_AppendAudioMediaSXY.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaSXY,self.Ptr, intPtrstream,X,Y)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def InsertAudioMedia(self ,index:int,stream:Stream,rectangle:RectangleF):
        """
    <summary>
        Insert an audio to collection.
    </summary>
    <param name="index">Index to inserted.</param>
    <param name="stream">Audio stream</param>
    <param name="rectangle">Rectangle should be inserted.</param>
        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertAudioMediaISR.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaISR,self.Ptr, index,intPtrstream,intPtrrectangle)


    def IndexOf(self ,shape:'IShape')->int:
        """
    <summary>
        Gets the index of the first occurrence of a shape in the collection.
    </summary>
    <param name="shape">Shape to found.</param>
    <returns>Index of the first occurrence of shape </returns>
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeList_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeList_IndexOf,self.Ptr, intPtrshape)
        return ret

#    @dispatch
#
#    def ToArray(self)->List[IShape]:
#        """
#    <summary>
#        Creates and returns an array with all shapse in it.
#    </summary>
#    <returns>Array of <see cref="T:Spire.Presentation.Shape" /></returns>
#        """
#        GetDllLibPpt().ShapeList_ToArray.argtypes=[c_void_p]
#        GetDllLibPpt().ShapeList_ToArray.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ShapeList_ToArray,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, IShape)
#        return ret


#    @dispatch
#
#    def ToArray(self ,startIndex:int,count:int)->List[IShape]:
#        """
#    <summary>
#        Creates and returns an array with all shapes from the specified range in it.
#                <param name="startIndex">An index of a first shape to return.</param>    <param name="count">A number of shapes to return.</param></summary>
#    <returns>Array of <see cref="T:Spire.Presentation.Shape" /></returns>
#        """
#        
#        GetDllLibPpt().ShapeList_ToArraySC.argtypes=[c_void_p ,c_int,c_int]
#        GetDllLibPpt().ShapeList_ToArraySC.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ShapeList_ToArraySC,self.Ptr, startIndex,count)
#        ret = GetObjVectorFromArray(intPtrArray, IShape)
#        return ret


    @dispatch

    def ZOrder(self ,index:int,shape:IShape):
        """
    <summary>
        Change a shape's zorder.
    </summary>
    <param name="index">Target index.</param>
    <param name="shape">Shape to move.</param>
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_ZOrder.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_ZOrder,self.Ptr, index,intPtrshape)

#    @dispatch
#
#    def ZOrder(self ,index:int,shapes:'IShape[]'):
#        """
#    <summary>
#        Change shapes's zorder.
#    </summary>
#    <param name="index">target index.</param>
#    <param name="shapes">shapes to move.</param>
#        """
#        #arrayshapes:ArrayTypeshapes = ""
#        countshapes = len(shapes)
#        ArrayTypeshapes = c_void_p * countshapes
#        arrayshapes = ArrayTypeshapes()
#        for i in range(0, countshapes):
#            arrayshapes[i] = shapes[i].Ptr
#
#
#        GetDllLibPpt().ShapeList_ZOrderIS.argtypes=[c_void_p ,c_int,ArrayTypeshapes]
#        CallCFunction(GetDllLibPpt().ShapeList_ZOrderIS,self.Ptr, index,arrayshapes)


    #@dispatch

    def AppendShape(self ,shapeType:ShapeType,rectangle:RectangleF)->'IAutoShape':
        """
    <summary>
        Adds a new shape to list.
    </summary>
    <param name="shapeType">Shape type</param>
    <param name="rectangle">Rectangle should be inserted.</param>
    <returns></returns>
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendShape.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().ShapeList_AppendShape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendShape,self.Ptr, enumshapeType,intPtrrectangle)
        ret = None if intPtr==None else IAutoShape(intPtr)
        return ret


   # @dispatch

    def AppendShapeByPoint(self ,shapeType:ShapeType,start:PointF,end:PointF)->'IAutoShape':
        """

        """
        enumshapeType:c_int = shapeType.value
        intPtrstart:c_void_p = start.Ptr
        intPtrend:c_void_p = end.Ptr

        GetDllLibPpt().ShapeList_AppendShapeSSE.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendShapeSSE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendShapeSSE,self.Ptr, enumshapeType,intPtrstart,intPtrend)
        ret = None if intPtr==None else IAutoShape(intPtr)
        return ret



    def AppendRoundRectangle(self ,x:float,y:float,width:float,height:float,radius:float)->'IAutoShape':
        """
    <summary>
        Adds a roundrectangle to list.
    </summary>
    <param name="x">X-coordinates of rectangle</param>
    <param name="y">Y-coordinates of rectangle</param>
    <param name="width">Width of rectangle</param>
    <param name="height">Height of rectangle</param>
    <param name="radius">Radius of rectangle</param>
        """
        
        GetDllLibPpt().ShapeList_AppendRoundRectangle.argtypes=[c_void_p ,c_float,c_float,c_float,c_float,c_float]
        GetDllLibPpt().ShapeList_AppendRoundRectangle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendRoundRectangle,self.Ptr, x,y,width,height,radius)
        ret = None if intPtr==None else IAutoShape(intPtr)
        return ret



    def InsertShape(self ,index:int,shapeType:'ShapeType',rectangle:'RectangleF'):
        """
    <summary>
        Insert a new shape to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="shapeType">Shape type</param>
    <param name="rectangle">Rectangle shoud be inserted.</param>
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertShape.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertShape,self.Ptr, index,enumshapeType,intPtrrectangle)


    def InsertRoundRectangle(self ,index:int,x:float,y:float,width:float,height:float,radius:float):
        """
    <summary>
        Insert a roundrectangle to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="x">X-coordinates of rectangle</param>
    <param name="y">Y-coordinates of rectangle</param>
    <param name="width">Width of rectangle</param>
    <param name="height">Height of rectangle</param>
    <param name="radius">Radius of rectangle</param>
        """
        
        GetDllLibPpt().ShapeList_InsertRoundRectangle.argtypes=[c_void_p ,c_int,c_float,c_float,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().ShapeList_InsertRoundRectangle,self.Ptr, index,x,y,width,height,radius)


    def AppendShapeConnector(self ,shapeType:'ShapeType',rectangle:'RectangleF')->'IShape':
        """
    <summary>
        Add new shape connector to collection.
    </summary>
    <param name="shapeType">Shape type</param>
    <param name="rectangle">Rectangle should be inserted.</param>
    <returns>Created shape</returns>
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendShapeConnector.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().ShapeList_AppendShapeConnector.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendShapeConnector,self.Ptr, enumshapeType,intPtrrectangle)
        ret = None if intPtr==None else IShape(intPtr)
        return ret



    def InsertShapeConnector(self ,index:int,shapeType:'ShapeType',rectangle:'RectangleF'):
        """
    <summary>
        Insert a new shape connector to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="shapeType">Shape type.</param>
    <param name="rectangle">Rectangle should be inserted.</param>
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertShapeConnector.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertShapeConnector,self.Ptr, index,enumshapeType,intPtrrectangle)

    def AppendEmbedImageByImageData(self ,shapeType:ShapeType,embedImage:'IImageData',rectangle:RectangleF)->'IEmbedImage':
        """
    <summary>
        Add a new embed image to List.
    </summary>
    <param name="shapeType"></param>
    <param name="embedImage"></param>
    <param name="rectangle"></param>
    <returns></returns>
        """
        enumshapeType:c_int = shapeType.value
        intPtrembedImage:c_void_p = embedImage.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendEmbedImage.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendEmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendEmbedImage,self.Ptr, enumshapeType,intPtrembedImage,intPtrrectangle)
        ret = None if intPtr==None else IEmbedImage(intPtr)
        return ret


    def AppendEmbedImageByPath(self ,shapeType:ShapeType,fileName:str,rectangle:RectangleF)->'IEmbedImage':
        """
    <summary>
        Add a new embed image to List.
    </summary>
    <param name="shapeType"></param>
    <param name="fileName"></param>
    <param name="rectangle"></param>
    <returns></returns>
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        fileNamePtr = StrToPtr(fileName)
        GetDllLibPpt().ShapeList_AppendEmbedImageSFR.argtypes=[c_void_p ,c_int,c_char_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendEmbedImageSFR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendEmbedImageSFR,self.Ptr, enumshapeType,fileNamePtr,intPtrrectangle)
        ret = None if intPtr==None else IEmbedImage(intPtr)
        return ret

    def AppendEmbedImageByStream(self ,shapeType:ShapeType,stream:Stream,rectangle:RectangleF)->'IEmbedImage':
        """
    <summary>
        Add a new embed image to List.
    </summary>
    <param name="shapeType"></param>
    <param name="embedImage"></param>
    <param name="rectangle"></param>
    <returns></returns>
        """
        enumshapeType:c_int = shapeType.value
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendEmbedImageSSR.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendEmbedImageSSR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendEmbedImageSSR,self.Ptr, enumshapeType,intPtrstream,intPtrrectangle)
        ret = None if intPtr==None else IEmbedImage(intPtr)
        return ret



    def InsertEmbedImage(self ,index:int,shapeType:'ShapeType',rectangle:'RectangleF',embedImage:'IImageData'):
        """
    <summary>
        Insert a embed image to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="shapeType">Shape type.</param>
    <param name="rectangle">Rectangle should be inserted.</param>
    <param name="embedImage">Embed image object.</param>
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr
        intPtrembedImage:c_void_p = embedImage.Ptr

        GetDllLibPpt().ShapeList_InsertEmbedImage.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertEmbedImage,self.Ptr, index,enumshapeType,intPtrrectangle,intPtrembedImage)


    def AddShape(self ,shape:'Shape'):
        """
    <summary>
        Add a shape to collection from slide.
    </summary>
    <param name="index">shape should be inserted.</param>
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_AddShape.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_AddShape,self.Ptr, intPtrshape)


    def AppendTable(self ,x:float,y:float,widths:List[float],heights:List[float])->'ITable':
        """
    <summary>
        Add a new table to collection.
    </summary>
    <param name="x"></param>
    <param name="y"></param>
    <param name="widths"></param>
    <param name="heights"></param>
    <returns></returns>
        """
        #arraywidths:ArrayTypewidths = ""
        countwidths = len(widths)
        ArrayTypewidths = c_double * countwidths
        arraywidths = ArrayTypewidths()
        for i in range(0, countwidths):
            arraywidths[i] = widths[i]

        #arrayheights:ArrayTypeheights = ""
        countheights = len(heights)
        ArrayTypeheights = c_double * countheights
        arrayheights = ArrayTypeheights()
        for i in range(0, countheights):
            arrayheights[i] = heights[i]


        GetDllLibPpt().ShapeList_AppendTable.argtypes=[c_void_p ,c_float,c_float,ArrayTypewidths,c_int,ArrayTypeheights,c_int]
        GetDllLibPpt().ShapeList_AppendTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendTable,self.Ptr, x,y,arraywidths,countwidths,arrayheights,countheights)
        ret = None if intPtr==None else ITable(intPtr)
        return ret



    def InsertTable(self ,index:int,x:float,y:float,columnWidths:List[float],rowHeights:List[float]):
        """
    <summary>
        Adds a new Table to collection.
    </summary>
    <param name="index">Index should be inserted.</param>
    <param name="x">Left side of shape.</param>
    <param name="y">Top side of shape.</param>
    <param name="columnWidths">Widths of columns in the table.</param>
    <param name="rowHeights">Heights of rows in the table.</param>
        """
        #arraycolumnWidths:ArrayTypecolumnWidths = ""
        countcolumnWidths = len(columnWidths)
        ArrayTypecolumnWidths = c_double * countcolumnWidths
        arraycolumnWidths = ArrayTypecolumnWidths()
        for i in range(0, countcolumnWidths):
            arraycolumnWidths[i] = columnWidths[i]

        #arrayrowHeights:ArrayTyperowHeights = ""
        countrowHeights = len(rowHeights)
        ArrayTyperowHeights = c_double * countrowHeights
        arrayrowHeights = ArrayTyperowHeights()
        for i in range(0, countrowHeights):
            arrayrowHeights[i] = rowHeights[i]


        GetDllLibPpt().ShapeList_InsertTable.argtypes=[c_void_p ,c_int,c_float,c_float,ArrayTypecolumnWidths,ArrayTyperowHeights]
        CallCFunction(GetDllLibPpt().ShapeList_InsertTable,self.Ptr, index,x,y,arraycolumnWidths,arrayrowHeights)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the element at the specified index of the collection.
    </summary>
    <param name="index">The zero-based index of the element to remove.</param>
        """
        
        GetDllLibPpt().ShapeList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ShapeList_RemoveAt,self.Ptr, index)


    def Remove(self ,shape:'IShape'):
        """
    <summary>
        Removes the first occurrence of a specific shape from the collection.
    </summary>
    <param name="shape">The shape to remove from the collection.</param>
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_Remove,self.Ptr, intPtrshape)

