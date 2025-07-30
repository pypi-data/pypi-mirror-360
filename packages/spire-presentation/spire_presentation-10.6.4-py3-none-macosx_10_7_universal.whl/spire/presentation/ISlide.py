from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ISlide (SpireObject) :
    """

    """
    @property

    def Theme(self)->'Theme':
        """
    <summary>
        Gets the theme object.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret


    @property
    def SlideNumber(self)->int:
        """
    <summary>
        Gets a number of slide.
            Index of slide in <see cref="P:Spire.Presentation.PresentationPptx.Slides" /> collection is always equal to SlideNumber - 1.
    </summary>
        """
        GetDllLibPpt().ISlide_get_SlideNumber.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideNumber.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISlide_get_SlideNumber,self.Ptr)
        return ret

    @SlideNumber.setter
    def SlideNumber(self, value:int):
        GetDllLibPpt().ISlide_set_SlideNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISlide_set_SlideNumber,self.Ptr, value)

    @property
    def Hidden(self)->bool:
        """
    <summary>
        Indicates whether the specified slide is hidden during a slide show.
            Read/write <see cref="T:System.Boolean" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Hidden.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Hidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISlide_get_Hidden,self.Ptr)
        return ret

    @Hidden.setter
    def Hidden(self, value:bool):
        GetDllLibPpt().ISlide_set_Hidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISlide_set_Hidden,self.Ptr, value)

    @property

    def NotesSlide(self)->'NotesSlide':
        """
    <summary>
        Gets the notes slide for the current slide.
            Read-only <see cref="P:Spire.Presentation.ISlide.NotesSlide" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_NotesSlide.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_NotesSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_NotesSlide,self.Ptr)
        ret = None if intPtr==None else NotesSlide(intPtr)
        return ret


    @property

    def Comments(self)->List['Comment']:
        """
    <summary>
        Gets all author comments.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Comments.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Comments.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_get_Comments,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, Comment)
        return ret


    @property

    def Shapes(self)->'ShapeCollection':
        """
    <summary>
        Gets the shapes of a slide.
            Read-only <see cref="T:Spire.Presentation.ShapeCollection" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
    <summary>
        Gets or sets the name of a slide.
            Read/write <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ISlide_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ISlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_set_Name,self.Ptr,valuePtr)

    @property

    def SlideID(self)->'int':
        """
    <summary>
        Gets the ID of a slide.
    </summary>
        """
        GetDllLibPpt().ISlide_get_SlideID.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideID.restype=c_int
        slideid = CallCFunction(GetDllLibPpt().ISlide_get_SlideID,self.Ptr)
        return slideid


    @property

    def MasterSlideID(self)->'int':
        """
    <summary>
        Gets the ID of a masterslide.
            Read-only <see cref="T:System.UInt32" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_MasterSlideID.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_MasterSlideID.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_MasterSlideID,self.Ptr)
        ret = None if intPtr==None else int(intPtr)
        return ret


    @MasterSlideID.setter
    def MasterSlideID(self, value:'UInt32'):
        GetDllLibPpt().ISlide_set_MasterSlideID.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_set_MasterSlideID,self.Ptr, value.Ptr)

    @property

    def TagsList(self)->'TagCollection':
        """
    <summary>
        Gets the slide's tags collection.
            Read-only <see cref="T:Spire.Presentation.Collections.TagCollection" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Timeline(self)->'TimeLine':
        """
    <summary>
        Gets animation timeline object.
            Read-only <see cref="T:Spire.Presentation.Drawing.TimeLine.TimeLine" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Timeline.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Timeline.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Timeline,self.Ptr)
        ret = None if intPtr==None else TimeLine(intPtr)
        return ret


    @property

    def SlideShowTransition(self)->'SlideShowTransition':
        """
    <summary>
        Gets the Transition object which contains information about
            how the specified slide advances during a slide show.
            Read-only <see cref="P:Spire.Presentation.ISlide.SlideShowTransition" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_SlideShowTransition.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideShowTransition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_SlideShowTransition,self.Ptr)
        ret = None if intPtr==None else SlideShowTransition(intPtr)
        return ret


    @property

    def SlideBackground(self)->'SlideBackground':
        """
    <summary>
        Gets slide's background.
            Read only <see cref="P:Spire.Presentation.ISlide.SlideBackground" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_SlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_SlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def DisplaySlideBackground(self)->'SlideBackground':
        """
    <summary>
        Gets slide's display background.
            Read only <see cref="P:Spire.Presentation.ISlide.DisplaySlideBackground" />.
    </summary>
        """
        GetDllLibPpt().ISlide_get_DisplaySlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_DisplaySlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_DisplaySlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        from spire.presentation import Presentation
        GetDllLibPpt().ISlide_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property
    def ShowMasterShape(self)->bool:
        """
    <summary>
        Hide background graphics
    </summary>
        """
        GetDllLibPpt().ISlide_get_ShowMasterShape.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_ShowMasterShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISlide_get_ShowMasterShape,self.Ptr)
        return ret

    @ShowMasterShape.setter
    def ShowMasterShape(self, value:bool):
        GetDllLibPpt().ISlide_set_ShowMasterShape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISlide_set_ShowMasterShape,self.Ptr, value)


    def GetPlaceholderShapes(self,placeholder:Placeholder):
        rets = []
        GetDllLibPpt().ISlide_GetPlaceholderShapes.argtypes=[c_void_p,c_void_p,c_int]
        GetDllLibPpt().ISlide_GetPlaceholderShapes.restype= IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().ISlide_GetPlaceholderShapes,self.Ptr,placeholder.Ptr,0)
        ret = None if intPtrWithTypeName==None else ShapeList._create(intPtrWithTypeName)
        if(ret != None):
            rets.append(ret)

        GetDllLibPpt().ISlide_GetPlaceholderShapes.argtypes=[c_void_p,c_void_p,c_int]
        GetDllLibPpt().ISlide_GetPlaceholderShapes.restype= IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().ISlide_GetPlaceholderShapes,self.Ptr,placeholder.Ptr,1)
        ret = None if intPtrWithTypeName==None else ShapeList._create(intPtrWithTypeName)
        if(ret != None):
            rets.append(ret)

        return rets
    
    def SaveAsImage(self)->'Stream':
        """

        """
        GetDllLibPpt().ISlide_SaveAsImage.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_SaveAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret

    
    def SaveAsImageByWH(self ,width:int,height:int)->'Stream':
        """

        """
        
        GetDllLibPpt().ISlide_SaveAsImageWH.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ISlide_SaveAsImageWH.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveAsImageWH,self.Ptr, width,height)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    #@dispatch

    #def SaveAsEMF(self ,filePath:str):
    #    """

    #    """
        
    #    GetDllLibPpt().ISlide_SaveAsEMF.argtypes=[c_void_p ,c_wchar_p]
    #    CallCFunction(GetDllLibPpt().ISlide_SaveAsEMF,self.Ptr, filePath)

    #@dispatch

    #def SaveAsEMF(self)->Image:
    #    """

    #    """
    #    GetDllLibPpt().ISlide_SaveAsEMF1.argtypes=[c_void_p]
    #    GetDllLibPpt().ISlide_SaveAsEMF1.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveAsEMF1,self.Ptr)
    #    ret = None if intPtr==None else Image(intPtr)
    #    return ret


    #@dispatch

    #def SaveAsEMF(self ,filePath:str,width:int,height:int):
    #    """

    #    """
        
    #    GetDllLibPpt().ISlide_SaveAsEMFFWH.argtypes=[c_void_p ,c_wchar_p,c_int,c_int]
    #    CallCFunction(GetDllLibPpt().ISlide_SaveAsEMFFWH,self.Ptr, filePath,width,height)


    def SaveDisplayBackgroundAsImage(self)->'Stream':
        """
    <summary>
        Saves the Slide Display Background to image. 
    </summary>
        """
        GetDllLibPpt().ISlide_SaveDisplayBackgroundAsImage.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_SaveDisplayBackgroundAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveDisplayBackgroundAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveToFile(self ,file:str,fileFormat:'FileFormat'):
        """
    <summary>
        Saves the Slide to the specified file. 
    </summary>
    <param name="file">A string that contains the path of the file to which to save this document.</param>
    <param name="fileFormat">convert to fileFormat.</param>
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().ISlide_SaveToFile.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt().ISlide_SaveToFile,self.Ptr,filePtr,enumfileFormat)


    def SaveToSVG(self)->'Stream':
        """
    <summary>
        Save the slide to SVG format
    </summary>
    <returns>A byte array of SVG file-stream.</returns>
        """
        GetDllLibPpt().ISlide_SaveToSVG.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_SaveToSVG.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveToSVG,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def AddNotesSlide(self)->'NotesSlide':
        """
    <summary>
        Adds a new notes slide.
    </summary>
    <returns>
  <see cref="P:Spire.Presentation.Slide.NotesSlide" /> for this slide.</returns>
        """
        GetDllLibPpt().ISlide_AddNotesSlide.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_AddNotesSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_AddNotesSlide,self.Ptr)
        ret = None if intPtr==None else NotesSlide(intPtr)
        return ret


    @dispatch

    def AddComment(self ,author:ICommentAuthor,text:str,position:PointF,dateTime:DateTime):
        """
    <summary>
        Adds a new comment.
    </summary>
    <param name="ICommentAuthor">comment author</param>
    <param name="text">comment text</param>
    <param name="position">position</param>
    <param name="dateTime"></param>
        """
        intPtrauthor:c_void_p = author.Ptr
        intPtrposition:c_void_p = position.Ptr
        intPtrdateTime:c_void_p = dateTime.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_AddComment.argtypes=[c_void_p ,c_void_p,c_char_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_AddComment,self.Ptr, intPtrauthor,textPtr,intPtrposition,intPtrdateTime)

    @dispatch

    def AddComment(self ,comment:Comment):
        """
    <summary>
        Adds a new comment.
    </summary>
    <param name="comment"></param>
        """
        intPtrcomment:c_void_p = comment.Ptr

        GetDllLibPpt().ISlide_AddCommentC.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_AddCommentC,self.Ptr, intPtrcomment)

    @dispatch

    def DeleteComment(self ,comment:Comment):
        """
    <summary>
        Delete a comment.
    </summary>
    <param name="comment"></param>
        """
        intPtrcomment:c_void_p = comment.Ptr

        GetDllLibPpt().ISlide_DeleteComment.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteComment,self.Ptr, intPtrcomment)

    @dispatch

    def DeleteComment(self ,author:ICommentAuthor,text:str):
        """
    <summary>
        Delete comments of specific text or specific author.
    </summary>
    <param name="ICommentAuthor">author of comments to delete or null to delete all comments.</param>
    <param name="string">text of comments to delete or "" to delete all comments.</param>
        """
        intPtrauthor:c_void_p = author.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_DeleteCommentAT.argtypes=[c_void_p ,c_void_p,c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteCommentAT,self.Ptr, intPtrauthor,textPtr)

    @dispatch

    def DeleteComment(self ,author:ICommentAuthor):
        """
    <summary>
        Delete comments of specific author.
    </summary>
    <param name="ICommentAuthor">author of comments to delete</param>
    <param name="string">text of comments to delete or "" to delete all comments.</param>
        """
        intPtrauthor:c_void_p = author.Ptr

        GetDllLibPpt().ISlide_DeleteCommentA.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteCommentA,self.Ptr, intPtrauthor)

    @dispatch

    def DeleteComment(self ,text:str):
        """
    <summary>
        Delete comments of specific text.
    </summary>
    <param name="string">text of comments to delete or "" to delete all comments.</param>
        """
        
        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_DeleteCommentT.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteCommentT,self.Ptr,textPtr)

#    @dispatch
#
#    def GetComments(self ,author:ICommentAuthor,text:str)->List[Comment]:
#        """
#    <summary>
#        Returns all slide comments added by specific author or specific text.
#    </summary>
#    <param name="ICommentAuthor">author of comments to find or null to find all comments.</param>
#    <param name="string">text of comments to find or "" to find all comments.</param>
#    <returns>Array of <see cref="T:Spire.Presentation.Comment" />.</returns>
#        """
#        intPtrauthor:c_void_p = author.Ptr
#
#        GetDllLibPpt().ISlide_GetComments.argtypes=[c_void_p ,c_void_p,c_wchar_p]
#        GetDllLibPpt().ISlide_GetComments.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetComments,self.Ptr, intPtrauthor,text)
#        ret = GetObjVectorFromArray(intPtrArray, Comment)
#        return ret


#    @dispatch
#
#    def GetComments(self ,author:ICommentAuthor)->List[Comment]:
#        """
#    <summary>
#        Returns all slide comments added by specific author.
#    </summary>
#    <param name="ICommentAuthor">author of comments to find.</param>
#    <returns>Array of <see cref="T:Spire.Presentation.Comment" />.</returns>
#        """
#        intPtrauthor:c_void_p = author.Ptr
#
#        GetDllLibPpt().ISlide_GetCommentsA.argtypes=[c_void_p ,c_void_p]
#        GetDllLibPpt().ISlide_GetCommentsA.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetCommentsA,self.Ptr, intPtrauthor)
#        ret = GetObjVectorFromArray(intPtrArray, Comment)
#        return ret


#    @dispatch
#
#    def GetComments(self ,text:str)->List[Comment]:
#        """
#    <summary>
#        Returns all slide comments added by specific text.
#    </summary>
#    <param name="string">text of comments to find or "" to find all comments.</param>
#    <returns>Array of <see cref="T:Spire.Presentation.Comment" />.</returns>
#        """
#        
#        GetDllLibPpt().ISlide_GetCommentsT.argtypes=[c_void_p ,c_wchar_p]
#        GetDllLibPpt().ISlide_GetCommentsT.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetCommentsT,self.Ptr, text)
#        ret = GetObjVectorFromArray(intPtrArray, Comment)
#        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
    <summary>
        Applies extra color scheme to a slide.
    </summary>
    <param name="scheme"></param>
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().ISlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_ApplyTheme,self.Ptr, intPtrscheme)

    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().ISlide_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_Dispose,self.Ptr)

    @property

    def Layout(self)->'ILayout':
        """
    <summary>
        get or set the layout.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Layout.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Layout.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Layout,self.Ptr)
        ret = None if intPtr==None else ILayout(intPtr)
        return ret


    @Layout.setter
    def Layout(self, value:'ILayout'):
        GetDllLibPpt().ISlide_set_Layout.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_set_Layout,self.Ptr, value.Ptr)

#
    def GroupShapes(self ,shapeList:'List')->'GroupShape':
        """
    <summary>
        Combine multiple shape together.
    </summary>
    <param name="shapeList"></param>
        """
        countShapes = len(shapeList)
        ArrayTypeshapeList = c_void_p * countShapes
        arrayrectangles = ArrayTypeshapeList()
        for i in range(0, countShapes):
            arrayrectangles[i] = shapeList[i].Ptr

        GetDllLibPpt().ISlide_GroupShapes.argtypes=[c_void_p ,ArrayTypeshapeList,c_int]
        GetDllLibPpt().ISlide_GroupShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_GroupShapes,self.Ptr, arrayrectangles,countShapes)
        ret = None if intPtr==None else GroupShape(intPtr)
        return ret




    def Ungroup(self ,groupShape:'GroupShape'):
        """
    <summary>
        Ungroup the GroupShape.
    </summary>
    <param name="groupShape">the group shape which needs to ungroup.</param>
        """
        intPtrgroupShape:c_void_p = groupShape.Ptr

        GetDllLibPpt().ISlide_Ungroup.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_Ungroup,self.Ptr, intPtrgroupShape)


    def ReplaceFirstText(self ,matchedString:str,newValue:str,caseSensitive:bool):
        """
    <summary>
        Replaces first matched string with new value in the slide.
    </summary>
    <param name="matchedString">old value</param>
    <param name="newValue">new value</param>
    <param name="caseSensitive">case sensitive</param>
        """
        
        matchedStringPtr = StrToPtr(matchedString)
        newValuePtr = StrToPtr(newValue)
        GetDllLibPpt().ISlide_ReplaceFirstText.argtypes=[c_void_p ,c_char_p,c_char_p,c_bool]
        CallCFunction(GetDllLibPpt().ISlide_ReplaceFirstText,self.Ptr,matchedStringPtr,newValuePtr,caseSensitive)


    def ReplaceAllText(self ,matchedString:str,newValue:str,caseSensitive:bool):
        """
    <summary>
        Replaces all matched string with new value in the slide.
    </summary>
    <param name="matchedString">old value</param>
    <param name="newValue">new value</param>
    <param name="caseSensitive">case sensitive</param>
        """
        
        matchedStringPtr = StrToPtr(matchedString)
        newValuePtr = StrToPtr(newValue)
        GetDllLibPpt().ISlide_ReplaceAllText.argtypes=[c_void_p ,c_char_p,c_char_p,c_bool]
        CallCFunction(GetDllLibPpt().ISlide_ReplaceAllText,self.Ptr,matchedStringPtr,newValuePtr,caseSensitive)

    @property

    def Title(self)->str:
        """
    <summary>
        Gets or Sets the Title of silde.
    </summary>
        """
        GetDllLibPpt().ISlide_get_Title.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Title.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ISlide_get_Title,self.Ptr))
        return ret


    @Title.setter
    def Title(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ISlide_set_Title.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_set_Title,self.Ptr,valuePtr)

#
#    def GetPlaceholderShapes(self ,placeholder:'Placeholder')->List['IShape']:
#        """
#    <summary>
#        Gets the layout shape and master shape by placeholder.
#    </summary>
#    <param name="placeholder">The target placeholder.</param>
#    <returns></returns>
#        """
#        intPtrplaceholder:c_void_p = placeholder.Ptr
#
#        GetDllLibPpt().ISlide_GetPlaceholderShapes.argtypes=[c_void_p ,c_void_p]
#        GetDllLibPpt().ISlide_GetPlaceholderShapes.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetPlaceholderShapes,self.Ptr, intPtrplaceholder)
#        ret = GetObjVectorFromArray(intPtrArray, IShape)
#        return ret


#
#    def ReplaceTextWithRegex(self ,regex:'Regex',newValue:str):
#        """
#    <summary>
#        Replace text with regex.
#    </summary>
#        """
#        intPtrregex:c_void_p = regex.Ptr
#
#        GetDllLibPpt().ISlide_ReplaceTextWithRegex.argtypes=[c_void_p ,c_void_p,c_wchar_p]
#        CallCFunction(GetDllLibPpt().ISlide_ReplaceTextWithRegex,self.Ptr, intPtrregex,newValue)



    def GetAllTextFrame(self)->List[str]:
       """
    <summary>
        Get all text in the slide
    </summary>
    <returns></returns>
       """
       GetDllLibPpt().ISlide_GetAllTextFrame.argtypes=[c_void_p]
       GetDllLibPpt().ISlide_GetAllTextFrame.restype=IntPtrArray
       intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetAllTextFrame,self.Ptr)
       ret = GetStringPtrArray(intPtrArray)
       return ret




    def FindFirstTextAsRange(self ,text:str)->'TextRange':
        """
    <summary>
        Find first text as a TextRange.
    </summary>
    <param name="text">Found text.</param>
    <returns></returns>
        """
        
        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_FindFirstTextAsRange.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ISlide_FindFirstTextAsRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_FindFirstTextAsRange,self.Ptr,textPtr)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret
    
    @property
    def OleObjects(self)->'OleObjectCollection':
        """
        """
        
        GetDllLibPpt().ISlide_get_OleObjects.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_OleObjects.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_OleObjects,self.Ptr)
        ret = None if intPtr==None else OleObjectCollection(intPtr)
        return ret


