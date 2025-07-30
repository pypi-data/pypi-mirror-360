from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from spire.presentation import _Presentation
from ctypes import *
import abc

class Presentation (_Presentation) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().Presentation_CreatePresentation.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_CreatePresentation)
        super(Presentation, self).__init__(intPtr)
    def __del__(self):
        GetDllLibPpt().Presentation_Dispose.argtypes = [c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_Dispose,self.Ptr)
        super(Presentation, self).__del__()
    """
    <summary>
        Represents an Presentation document. 
    </summary>
    """
    @property

    def SlideSize(self)->'SlideSize':
        """
    <summary>
        Get slide size.
    </summary>
        """
        GetDllLibPpt().Presentation_get_SlideSize.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SlideSize,self.Ptr)
        ret = None if intPtr==None else SlideSize(intPtr)
        return ret


    @property

    def SectionList(self)->'SectionList':
        """

        """
        GetDllLibPpt().Presentation_get_SectionList.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SectionList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SectionList,self.Ptr)
        ret = None if intPtr==None else SectionList(intPtr)
        return ret



    def SetPageSize(self ,w:float,h:float,IsRatio:bool):
        """
    <summary>
        Set page size.
    </summary>
    <param name="w">Width or width ratio</param>
    <param name="h">Height or height ratio</param>
    <param name="IsRation">Is ratio</param>
        """
        
        GetDllLibPpt().Presentation_SetPageSize.argtypes=[c_void_p ,c_float,c_float,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetPageSize,self.Ptr, w,h,IsRatio)

    @property
    def StrictFirstAndLastCharacters(self)->bool:
        """

        """
        GetDllLibPpt().Presentation_get_StrictFirstAndLastCharacters.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_StrictFirstAndLastCharacters.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_StrictFirstAndLastCharacters,self.Ptr)
        return ret

    @StrictFirstAndLastCharacters.setter
    def StrictFirstAndLastCharacters(self, value:bool):
        GetDllLibPpt().Presentation_set_StrictFirstAndLastCharacters.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_StrictFirstAndLastCharacters,self.Ptr, value)

    @property

    def WavAudios(self)->'WavAudioCollection':
        """
    <summary>
        Gets the collection of all embedded audio.
    </summary>
        """
        GetDllLibPpt().Presentation_get_WavAudios.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_WavAudios.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_WavAudios,self.Ptr)
        ret = None if intPtr==None else WavAudioCollection(intPtr)
        return ret


    @property

    def Videos(self)->'VideoCollection':
        """
    <summary>
        Gets the collection of all embedded video.
    </summary>
        """
        GetDllLibPpt().Presentation_get_Videos.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Videos.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Videos,self.Ptr)
        ret = None if intPtr==None else VideoCollection(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
    <summary>
        Gets the tags collection.
    </summary>
        """
        GetDllLibPpt().Presentation_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Images(self)->'ImageCollection':
        """
    <summary>
        Gets the collection of all images.
    </summary>
        """
        GetDllLibPpt().Presentation_get_Images.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Images.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Images,self.Ptr)
        ret = None if intPtr==None else ImageCollection(intPtr)
        return ret


    @property

    def DocumentProperty(self)->'IDocumentProperty':
        """
    <summary>
        Gets Standard and custom document properties.
    </summary>
        """
        GetDllLibPpt().Presentation_get_DocumentProperty.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DocumentProperty.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_DocumentProperty,self.Ptr)
        ret = None if intPtr==None else IDocumentProperty(intPtr)
        return ret


    @property

    def CommentAuthors(self)->'CommentAuthorCollection':
        """
    <summary>
        Gets CommentAuthor List.
    </summary>
        """
        GetDllLibPpt().Presentation_get_CommentAuthors.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_CommentAuthors.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_CommentAuthors,self.Ptr)
        ret = None if intPtr==None else CommentAuthorCollection(intPtr)
        return ret


    @property
    def DFlag(self)->bool:
        """

        """
        GetDllLibPpt().Presentation_get_DFlag.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DFlag.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_DFlag,self.Ptr)
        return ret

    @DFlag.setter
    def DFlag(self, value:bool):
        GetDllLibPpt().Presentation_set_DFlag.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_DFlag,self.Ptr, value)

    @property

    def FormatAndVersion(self)->'FormatAndVersion':
        """
    <summary>
        Gets the the Format and Version of file;
            read-only
    </summary>
        """
        GetDllLibPpt().Presentation_get_FormatAndVersion.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_FormatAndVersion.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_FormatAndVersion,self.Ptr)
        objwraped = FormatAndVersion(ret)
        return objwraped

#
#    def AddDigitalSignature(self ,certificate:'X509Certificate2',comments:str,signTime:'DateTime')->'IDigitalSignatures':
#        """
#    <summary>
#        Add a DigitalSignature.
#    </summary>
#    <param name="certificate">Certificate object that was used to sign</param>
#    <param name="comments">Signature Comments</param>
#    <param name="signTime">Sign Time</param>
#    <returns>Collection of DigitalSignature</returns>
#        """
#        intPtrcertificate:c_void_p = certificate.Ptr
#        intPtrsignTime:c_void_p = signTime.Ptr
#
#        GetDllLibPpt().Presentation_AddDigitalSignature.argtypes=[c_void_p ,c_void_p,c_wchar_p,c_void_p]
#        GetDllLibPpt().Presentation_AddDigitalSignature.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().Presentation_AddDigitalSignature,self.Ptr, intPtrcertificate,comments,intPtrsignTime)
#        ret = None if intPtr==None else IDigitalSignatures(intPtr)
#        return ret
#



    def GetDigitalSignatures(self)->'IDigitalSignatures':
        """
    <summary>
        Get collection of DigitalSignature in this file.
    </summary>
    <returns>Collection of DigitalSignature</returns>
        """
        GetDllLibPpt().Presentation_GetDigitalSignatures.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_GetDigitalSignatures.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_GetDigitalSignatures,self.Ptr)
        ret = None if intPtr==None else IDigitalSignatures(intPtr)
        return ret


    def RemoveAllDigitalSignatures(self):
        """
    <summary>
        Remove all DigitalSignature in this file.
    </summary>
        """
        GetDllLibPpt().Presentation_RemoveAllDigitalSignatures.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_RemoveAllDigitalSignatures,self.Ptr)

    @property
    def IsDigitallySigned(self)->bool:
        """
    <summary>
        Indicates whether this spreadsheet is digitally signed.
    </summary>
        """
        GetDllLibPpt().Presentation_get_IsDigitallySigned.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_IsDigitallySigned.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_IsDigitallySigned,self.Ptr)
        return ret


    def SetCustomFontsFolder(self ,fontsFolder:str):
        """
    <summary>
        Set folder where the custom font is located.
                <param name="fontsFolder">the fonts folfer.</param></summary>
        """
        
        fontsFolderPtr = StrToPtr(fontsFolder)
        GetDllLibPpt().Presentation_SetCustomFontsFolder.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_SetCustomFontsFolder,self.Ptr,fontsFolderPtr)

    @dispatch

    def IsPasswordProtected(self ,fileName:str)->bool:
        """
    <summary>
        Determine whether the document is encrypted
    </summary>
        """
        
        fileNamePtr = StrToPtr(fileName)
        GetDllLibPpt().Presentation_IsPasswordProtected.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().Presentation_IsPasswordProtected.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_IsPasswordProtected,self.Ptr,fileNamePtr)
        return ret

    @dispatch

    def IsPasswordProtected(self ,stream:Stream)->bool:
        """
    <summary>
        Determine whether the document is encrypted
                <param name="stream">file stream</param></summary>
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().Presentation_IsPasswordProtectedS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Presentation_IsPasswordProtectedS.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_IsPasswordProtectedS,self.Ptr, intPtrstream)
        return ret

    @property
    def HighQualityImage(self)->bool:
        """
    <summary>
        Determine whether the document is encrypted
                <param name="stream">file stream</param></summary>
        """
        GetDllLibPpt().Presentation_get_HighQualityImage.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_HighQualityImage.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_HighQualityImage,self.Ptr)
        return ret

    @HighQualityImage.setter
    def HighQualityImage(self, value:bool):
        GetDllLibPpt().Presentation_set_HighQualityImage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_HighQualityImage,self.Ptr, value)

    
    def SlideSizeAutoFit(self, value:bool):
        GetDllLibPpt().Presentation_set_SlideSizeAutoFit.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideSizeAutoFit,self.Ptr, value)

    def Dispose(self):
        """

        """
        GetDllLibPpt().Presentation_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_Dispose,self.Ptr)

    @property

    def SaveToPdfOption(self)->'SaveToPdfOption':
        """
    <summary>
        SaveToPdfOption
    </summary>
        """
        GetDllLibPpt().Presentation_get_SaveToPdfOption.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveToPdfOption.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SaveToPdfOption,self.Ptr)
        ret = None if intPtr==None else SaveToPdfOption(intPtr)
        return ret


    @SaveToPdfOption.setter
    def SaveToPdfOption(self, value:'SaveToPdfOption'):
        GetDllLibPpt().Presentation_set_SaveToPdfOption.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveToPdfOption,self.Ptr, value.Ptr)

    @property

    def SaveToHtmlOption(self)->'SaveToHtmlOption':
        """

        """
        GetDllLibPpt().Presentation_get_SaveToHtmlOption.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveToHtmlOption.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SaveToHtmlOption,self.Ptr)
        ret = None if intPtr==None else SaveToHtmlOption(intPtr)
        return ret


    @SaveToHtmlOption.setter
    def SaveToHtmlOption(self, value:'SaveToHtmlOption'):
        GetDllLibPpt().Presentation_set_SaveToHtmlOption.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveToHtmlOption,self.Ptr, value.Ptr)

    @property

    def SaveToPptxOption(self)->'SaveToPptxOption':
        """
    <summary>
        save to pptx option.
    </summary>
        """
        GetDllLibPpt().Presentation_get_SaveToPptxOption.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveToPptxOption.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SaveToPptxOption,self.Ptr)
        ret = None if intPtr==None else SaveToPptxOption(intPtr)
        return ret


    @SaveToPptxOption.setter
    def SaveToPptxOption(self, value:'SaveToPptxOption'):
        GetDllLibPpt().Presentation_set_SaveToPptxOption.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveToPptxOption,self.Ptr, value.Ptr)


    def FindSlide(self ,id:int)->'ISlide':
        """
    <summary>
        Find a slide by ID.
    </summary>
    <param name="id"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().Presentation_FindSlide.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().Presentation_FindSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_FindSlide,self.Ptr, id)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


#
#    def GetBytes(self)->List['Byte']:
#        """
#    <summary>
#        Converts the document to an array of bytes. 
#    </summary>
#    <returns>An array of bytes.</returns>
#        """
#        GetDllLibPpt().Presentation_GetBytes.argtypes=[c_void_p]
#        GetDllLibPpt().Presentation_GetBytes.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().Presentation_GetBytes,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret



    def GetStream(self)->'Stream':
        """
    <summary>
        Gets the document as a stream to read from.
    </summary>
    <returns>A <see cref="T:System.IO.Stream" /> to read from.</returns>
        """
        GetDllLibPpt().Presentation_GetStream.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_GetStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_GetStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat):
        """
    <summary>
        Opens the document from a stream.
    </summary>
    <param name="stream">The document stream.</param>
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt().Presentation_LoadFromStream.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromStream,self.Ptr, intPtrstream,enumfileFormat)

    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat,password:str):
        """
    <summary>
        Opens the document from a stream.
    </summary>
    <param name="stream">The document stream.</param>
    <param name="fileFormat">The file format</param>
    <param name="password">The password.</param>
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_LoadFromStreamSFP.argtypes=[c_void_p ,c_void_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromStreamSFP,self.Ptr, intPtrstream,enumfileFormat,passwordPtr)

    @dispatch

    def LoadFromFile(self ,file:str):
        """
    <summary>
        Opens the document from a file.
    </summary>
    <param name="file">The document file path.</param>
        """
        
        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_LoadFromFile.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFile,self.Ptr,filePtr)

    @dispatch

    def LoadFromFile(self ,file:str,password:str):
        """
    <summary>
        Opens the document from a file.
    </summary>
    <param name="file">The document file path.</param>
        """
        
        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_LoadFromFileFP.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFileFP,self.Ptr,filePtr,passwordPtr)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat):
        """

        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_LoadFromFileFF.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFileFF,self.Ptr,filePtr,enumfileFormat)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat,password:str):
        """

        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_LoadFromFileFFP.argtypes=[c_void_p ,c_char_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFileFFP,self.Ptr,filePtr,enumfileFormat,passwordPtr)

    @dispatch

    def SaveToFile(self ,stream:Stream,fileFormat:FileFormat):
        """
    <summary>
        Saves the document to the specified stream. 
    </summary>
    <param name="stream">The <see cref="T:System.IO.Stream" /> where the document will be saved.</param>
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt().Presentation_SaveToFile.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_SaveToFile,self.Ptr, intPtrstream,enumfileFormat)


    def SaveToSVG(self)->List[Stream]:
       """
   <summary>
       Saves the document to the SVG Format. 
   </summary>
       """
       GetDllLibPpt().Presentation_SaveToSVG.argtypes=[c_void_p]
       GetDllLibPpt().Presentation_SaveToSVG.restype=IntPtrArray
       intPtrArray = CallCFunction(GetDllLibPpt().Presentation_SaveToSVG,self.Ptr)
       ret = GetObjVectorFromArray(intPtrArray,Stream)
       return ret




    def OnlineSaveToFile(self ,file:str,fileFormat:'FileFormat')->bool:
        """
    <summary>
        used for online. 
    </summary>
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_OnlineSaveToFile.argtypes=[c_void_p ,c_char_p,c_int]
        GetDllLibPpt().Presentation_OnlineSaveToFile.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_OnlineSaveToFile,self.Ptr,filePtr,enumfileFormat)
        return ret

    @dispatch

    def SaveToFile(self ,file:str,fileFormat:FileFormat):
        """
    <summary>
        Saves the document to the specified file. 
    </summary>
    <param name="file">A string that contains the path of the file to which to save this document.</param>
    <param name="fileFormat">convert to fileFormat.</param>
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_SaveToFileFF.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_SaveToFileFF,self.Ptr,filePtr,enumfileFormat)

#    @dispatch
#
#    def SaveToHttpResponse(self ,FileName:str,fileFormat:FileFormat,response:'HttpResponse'):
#        """
#    <summary>
#        Save Presation to the http response.
#    </summary>
#    <param name="FileName">File Name</param>
#    <param name="response">Http response</param>
#    <param name="saveType">Save type : attachment or inline mode</param>
#        """
#        enumfileFormat:c_int = fileFormat.value
#        intPtrresponse:c_void_p = response.Ptr
#
#        GetDllLibPpt().Presentation_SaveToHttpResponse.argtypes=[c_void_p ,c_wchar_p,c_int,c_void_p]
#        CallCFunction(GetDllLibPpt().Presentation_SaveToHttpResponse,self.Ptr, FileName,enumfileFormat,intPtrresponse)


#    @dispatch
#
#    def SaveToHttpResponse(self ,FileName:str,fileFormat:FileFormat,response:'HttpResponse',isInlineMode:bool):
#        """
#    <summary>
#        Save Presation to the http response.
#    </summary>
#    <param name="FileName">File name</param>
#    <param name="response">Http response.</param>
#    <param name="isInlineMode">True - inline mode, False - Attachment mode.</param>
#        """
#        enumfileFormat:c_int = fileFormat.value
#        intPtrresponse:c_void_p = response.Ptr
#
#        GetDllLibPpt().Presentation_SaveToHttpResponseFFRI.argtypes=[c_void_p ,c_wchar_p,c_int,c_void_p,c_bool]
#        CallCFunction(GetDllLibPpt().Presentation_SaveToHttpResponseFFRI,self.Ptr, FileName,enumfileFormat,intPtrresponse,isInlineMode)



    def Encrypt(self ,password:str):
        """
    <summary>
        Encrypts with specified password.
    </summary>
    <param name="password">The password.</param>
        """
        
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_Encrypt.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_Encrypt,self.Ptr,passwordPtr)

    def RemoveEncryption(self):
        """
    <summary>
        Removes the encryption.
    </summary>
        """
        GetDllLibPpt().Presentation_RemoveEncryption.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_RemoveEncryption,self.Ptr)


    def Protect(self ,password:str):
        """
    <summary>
        Protection for this presentation.
    </summary>
    <param name="password">The password.</param>
        """
        
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_Protect.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_Protect,self.Ptr,passwordPtr)

    def RemoveProtect(self):
        """
    <summary>
        Remove proection.
    </summary>
        """
        GetDllLibPpt().Presentation_RemoveProtect.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_RemoveProtect,self.Ptr)

    #@dispatch

    #def Print(self ,presentationPrintDocument:PresentationPrintDocument):
    #    """

    #    """
    #    intPtrpresentationPrintDocument:c_void_p = presentationPrintDocument.Ptr

    #    GetDllLibPpt().Presentation_Print.argtypes=[c_void_p ,c_void_p]
    #    CallCFunction(GetDllLibPpt().Presentation_Print,self.Ptr, intPtrpresentationPrintDocument)

#    @dispatch
#
#    def Print(self ,printerSettings:'PrinterSettings'):
#        """
#    <summary>
#        Prints the presentation according to the specified printer settings.
#    </summary>
#    <param name="printerSettings">Printer settings to use.</param>
#        """
#        intPtrprinterSettings:c_void_p = printerSettings.Ptr
#
#        GetDllLibPpt().Presentation_PrintP.argtypes=[c_void_p ,c_void_p]
#        CallCFunction(GetDllLibPpt().Presentation_PrintP,self.Ptr, intPtrprinterSettings)


#    @dispatch
#
#    def Print(self ,printerSettings:'PrinterSettings',presName:str):
#        """
#    <summary>
#        Prints the document according to the specified printer settings, using
#            the standard (no User Interface) print controller and a presentation name.
#    </summary>
#    <param name="printerSettings">The .NET printer settings to use.</param>
#    <param name="presName">The presentation name to display (for example, in a print
#            status dialog box or printer queue) while printing the presentation.</param>
#        """
#        intPtrprinterSettings:c_void_p = printerSettings.Ptr
#
#        GetDllLibPpt().Presentation_PrintPP.argtypes=[c_void_p ,c_void_p,c_wchar_p]
#        CallCFunction(GetDllLibPpt().Presentation_PrintPP,self.Ptr, intPtrprinterSettings,presName)


    #@dispatch

    #def Print(self ,Name:str):
    #    """
    #<summary>
    #    Print the whole presentation to the specified printer.
    #</summary>
    #<param name="Name">The name of the printer.</param>
    #    """
        
    #    GetDllLibPpt().Presentation_PrintN.argtypes=[c_void_p ,c_wchar_p]
    #    CallCFunction(GetDllLibPpt().Presentation_PrintN,self.Ptr, Name)


    def SetFooterText(self ,text:str):
        """

        """
        
        textPtr = StrToPtr(text)
        GetDllLibPpt().Presentation_SetFooterText.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_SetFooterText,self.Ptr,textPtr)

    @dispatch

    def SetDateTime(self ,dateTime:DateTime):
        """

        """
        intPtrdateTime:c_void_p = dateTime.Ptr

        GetDllLibPpt().Presentation_SetDateTime.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_SetDateTime,self.Ptr, intPtrdateTime)

    @dispatch

    def SetDateTime(self ,dateTime:DateTime,format:str):
        """

        """
        intPtrdateTime:c_void_p = dateTime.Ptr

        formatPtr = StrToPtr(format)
        GetDllLibPpt().Presentation_SetDateTimeDF.argtypes=[c_void_p ,c_void_p,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_SetDateTimeDF,self.Ptr, intPtrdateTime,formatPtr)


    def SetFooterVisible(self ,visible:bool):
        """

        """
        
        GetDllLibPpt().Presentation_SetFooterVisible.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetFooterVisible,self.Ptr, visible)


    def SetDateTimeVisible(self ,visible:bool):
        """

        """
        
        GetDllLibPpt().Presentation_SetDateTimeVisible.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetDateTimeVisible,self.Ptr, visible)


    def SetSlideNoVisible(self ,visible:bool):
        """

        """
        
        GetDllLibPpt().Presentation_SetSlideNoVisible.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetSlideNoVisible,self.Ptr, visible)

    @property
    def SlideNumberVisible(self)->bool:
        """
    <summary>
        Gets or sets value .Specifies whether the slide number placeholder is enabled for this master
    </summary>
        """
        GetDllLibPpt().Presentation_get_SlideNumberVisible.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideNumberVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SlideNumberVisible,self.Ptr)
        return ret

    @SlideNumberVisible.setter
    def SlideNumberVisible(self, value:bool):
        GetDllLibPpt().Presentation_set_SlideNumberVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideNumberVisible,self.Ptr, value)

    @property
    def DateTimeVisible(self)->bool:
        """
    <summary>
        Gets or sets value .Specifies whether Date-Time placeholder is enabled for this master
    </summary>
        """
        GetDllLibPpt().Presentation_get_DateTimeVisible.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DateTimeVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_DateTimeVisible,self.Ptr)
        return ret

    @DateTimeVisible.setter
    def DateTimeVisible(self, value:bool):
        GetDllLibPpt().Presentation_set_DateTimeVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_DateTimeVisible,self.Ptr, value)

    @property
    def FooterVisible(self)->bool:
        """
    <summary>
        Gets or sets value .Specifies whether the Footer placeholder is enabled for this master
    </summary>
        """
        GetDllLibPpt().Presentation_get_FooterVisible.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_FooterVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_FooterVisible,self.Ptr)
        return ret

    @FooterVisible.setter
    def FooterVisible(self, value:bool):
        GetDllLibPpt().Presentation_set_FooterVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_FooterVisible,self.Ptr, value)

    @property
    def AutoCompressPictures(self)->bool:
        """
    <summary>
        Indicates that Compress Pictures feature automatically reduces the file size of pictures.
    </summary>
        """
        GetDllLibPpt().Presentation_get_AutoCompressPictures.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_AutoCompressPictures.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_AutoCompressPictures,self.Ptr)
        return ret

    @AutoCompressPictures.setter
    def AutoCompressPictures(self, value:bool):
        GetDllLibPpt().Presentation_set_AutoCompressPictures.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_AutoCompressPictures,self.Ptr, value)

    @property
    def BookmarkIdSeed(self)->int:
        """
    <summary>
        Bookmark ID Seed.
    </summary>
        """
        GetDllLibPpt().Presentation_get_BookmarkIdSeed.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_BookmarkIdSeed.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_BookmarkIdSeed,self.Ptr)
        return ret

    @BookmarkIdSeed.setter
    def BookmarkIdSeed(self, value:int):
        GetDllLibPpt().Presentation_set_BookmarkIdSeed.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_BookmarkIdSeed,self.Ptr, value)

    @property

    def DefaultTextStyle(self)->'TextStyle':
        """
    <summary>
        Default paragraph and list style.
    </summary>
        """
        GetDllLibPpt().Presentation_get_DefaultTextStyle.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DefaultTextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_DefaultTextStyle,self.Ptr)
        ret = None if intPtr==None else TextStyle(intPtr)
        return ret


    @property
    def ShowNarration(self)->bool:
        """
    <summary>
        Specifies whether slide show narration should be played when presenting
    </summary>
        """
        GetDllLibPpt().Presentation_get_ShowNarration.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowNarration.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowNarration,self.Ptr)
        return ret

    @ShowNarration.setter
    def ShowNarration(self, value:bool):
        GetDllLibPpt().Presentation_set_ShowNarration.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowNarration,self.Ptr, value)

    @property
    def ShowAnimation(self)->bool:
        """
    <summary>
        Specifies whether slide show animation should be shown when presenting
    </summary>
        """
        GetDllLibPpt().Presentation_get_ShowAnimation.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowAnimation.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowAnimation,self.Ptr)
        return ret

    @ShowAnimation.setter
    def ShowAnimation(self, value:bool):
        GetDllLibPpt().Presentation_set_ShowAnimation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowAnimation,self.Ptr, value)

    @property
    def ShowLoop(self)->bool:
        """
    <summary>
        Specifies whether the slide show should be set to loop at the end
    </summary>
        """
        GetDllLibPpt().Presentation_get_ShowLoop.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowLoop.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowLoop,self.Ptr)
        return ret

    @ShowLoop.setter
    def ShowLoop(self, value:bool):
        GetDllLibPpt().Presentation_set_ShowLoop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowLoop,self.Ptr, value)

    @property
    def HasMacros(self)->bool:
        """
    <summary>
        Specifies whether contains VBA macros.
    </summary>
        """
        GetDllLibPpt().Presentation_get_HasMacros.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_HasMacros.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_HasMacros,self.Ptr)
        return ret

    def DeleteMacros(self):
        """
    <summary>
        Delete the Macros
    </summary>
        """
        GetDllLibPpt().Presentation_DeleteMacros.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_DeleteMacros,self.Ptr)

    @property

    def ShowType(self)->'SlideShowType':
        """
    <summary>
        Specifies the slide show type
    </summary>
        """
        GetDllLibPpt().Presentation_get_ShowType.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowType,self.Ptr)
        objwraped = SlideShowType(ret)
        return objwraped

    @ShowType.setter
    def ShowType(self, value:'SlideShowType'):
        GetDllLibPpt().Presentation_set_ShowType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowType,self.Ptr, value.value)

    @property
    def UseTimings(self)->bool:
        """
    <summary>
        Specifies whether slide transition timing should be used to advance slides when presenting
    </summary>
        """
        GetDllLibPpt().Presentation_get_UseTimings.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_UseTimings.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_UseTimings,self.Ptr)
        return ret

    @UseTimings.setter
    def UseTimings(self, value:bool):
        GetDllLibPpt().Presentation_set_UseTimings.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_UseTimings,self.Ptr, value)

    @property
    def EmbedTrueTypeFonts(self)->bool:
        """
    <summary>
        Indicates whther embeds TrueType fonts in a document when it's saved.
    </summary>
        """
        GetDllLibPpt().Presentation_get_EmbedTrueTypeFonts.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_EmbedTrueTypeFonts.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_EmbedTrueTypeFonts,self.Ptr)
        return ret

    @EmbedTrueTypeFonts.setter
    def EmbedTrueTypeFonts(self, value:bool):
        GetDllLibPpt().Presentation_set_EmbedTrueTypeFonts.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_EmbedTrueTypeFonts,self.Ptr, value)

    @property
    def FirstSlideNumber(self)->int:
        """
    <summary>
        Slide number that appears on the first slide in your presentation.
    </summary>
        """
        GetDllLibPpt().Presentation_get_FirstSlideNumber.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_FirstSlideNumber.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_FirstSlideNumber,self.Ptr)
        return ret

    @FirstSlideNumber.setter
    def FirstSlideNumber(self, value:int):
        GetDllLibPpt().Presentation_set_FirstSlideNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_FirstSlideNumber,self.Ptr, value)

    @property

    def HandoutMaster(self)->'INoteMasterSlide':
        """
    <summary>
        Gets a master for all notes slides of this presentation.
    </summary>
        """
        GetDllLibPpt().Presentation_get_HandoutMaster.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_HandoutMaster.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_HandoutMaster,self.Ptr)
        ret = None if intPtr==None else INoteMasterSlide(intPtr)
        return ret


    @property

    def NotesMaster(self)->'INoteMasterSlide':
        """
    <summary>
        Gets a master for all notes slides of this presentation.
    </summary>
        """
        GetDllLibPpt().Presentation_get_NotesMaster.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_NotesMaster.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_NotesMaster,self.Ptr)
        ret = None if intPtr==None else INoteMasterSlide(intPtr)
        return ret


    @property

    def NotesSlideSize(self)->'SizeF':
        """
    <summary>
        Gets note slide size object.
    </summary>
        """
        GetDllLibPpt().Presentation_get_NotesSlideSize.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_NotesSlideSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_NotesSlideSize,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @property
    def SaveSubsetFonts(self)->bool:
        """
    <summary>
        Indicates whther embeds subset TrueType fonts in a document when it's saved.
    </summary>
        """
        GetDllLibPpt().Presentation_get_SaveSubsetFonts.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveSubsetFonts.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SaveSubsetFonts,self.Ptr)
        return ret

    @SaveSubsetFonts.setter
    def SaveSubsetFonts(self, value:bool):
        GetDllLibPpt().Presentation_set_SaveSubsetFonts.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveSubsetFonts,self.Ptr, value)

    @property
    def ServerZoom(self)->float:
        """
    <summary>
        Specifies a zoom level for visual representations of the document.
    </summary>
        """
        GetDllLibPpt().Presentation_get_ServerZoom.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ServerZoom.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ServerZoom,self.Ptr)
        return ret

    @ServerZoom.setter
    def ServerZoom(self, value:float):
        GetDllLibPpt().Presentation_set_ServerZoom.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Presentation_set_ServerZoom,self.Ptr, value)

    @property

    def Masters(self)->'MasterSlideCollection':
        """
    <summary>
        Gets a list of all master slides.
    </summary>
        """
        GetDllLibPpt().Presentation_get_Masters.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Masters.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Masters,self.Ptr)
        ret = None if intPtr==None else MasterSlideCollection(intPtr)
        return ret


    @property

    def Slides(self)->'SlideCollection':
        """
    <summary>
        Gets a list of all slides.
    </summary>
        """
        GetDllLibPpt().Presentation_get_Slides.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Slides.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Slides,self.Ptr)
        ret = None if intPtr==None else SlideCollection(intPtr)
        return ret
    
    @property

    def SlideCountPerPageForPrint(self)->'PageSlideCount':
        """
    <summary>
        Number of total slides per page.
    </summary>
        """
        GetDllLibPpt().Presentation_get_SlideCountPerPageForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideCountPerPageForPrint.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SlideCountPerPageForPrint,self.Ptr)
        objwraped = PageSlideCount(ret)
        return objwraped

    @SlideCountPerPageForPrint.setter
    def SlideCountPerPageForPrint(self, value:'PageSlideCount'):
        GetDllLibPpt().Presentation_set_SlideCountPerPageForPrint.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideCountPerPageForPrint,self.Ptr, value.value)

    def SelectSlidesForPrint(self ,selectSlidesForPrint:List[str]):
        """
    <summary>
        Select print slides
    </summary>
        """
        #arrayselectSlidesForPrint:ArrayTypeselectSlidesForPrint = ""
        countselectSlidesForPrint = len(selectSlidesForPrint)
        ArrayTypeselectSlidesForPrint = c_wchar_p * countselectSlidesForPrint
        arrayselectSlidesForPrint = ArrayTypeselectSlidesForPrint()
        for i in range(0, countselectSlidesForPrint):
            arrayselectSlidesForPrint[i] = selectSlidesForPrint[i]


        GetDllLibPpt().Presentation_SelectSlidesForPrint.argtypes=[c_void_p ,ArrayTypeselectSlidesForPrint]
        CallCFunction(GetDllLibPpt().Presentation_SelectSlidesForPrint,self.Ptr, arrayselectSlidesForPrint)
        

    @property

    def OrderForPrint(self)->'Order':
        """
    <summary>
        The order of Print.
    </summary>
        """
        GetDllLibPpt().Presentation_get_OrderForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_OrderForPrint.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_OrderForPrint,self.Ptr)
        objwraped = Order(ret)
        return objwraped

    @OrderForPrint.setter
    def OrderForPrint(self, value:'Order'):
        GetDllLibPpt().Presentation_set_OrderForPrint.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_OrderForPrint,self.Ptr, value.value)
      
    @property
    def SlideFrameForPrint(self)->bool:
        """
    <summary>
        Whether to set slideFrame for printing.
    </summary>
        """
        GetDllLibPpt().Presentation_get_SlideFrameForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideFrameForPrint.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SlideFrameForPrint,self.Ptr)
        return ret

    @SlideFrameForPrint.setter
    def SlideFrameForPrint(self, value:bool):
        GetDllLibPpt().Presentation_set_SlideFrameForPrint.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideFrameForPrint,self.Ptr, value)
   
    @property
    def GrayLevelForPrint(self)->bool:
        """
    <summary>
        Whether to set gray level for printing
    </summary>
        """
        GetDllLibPpt().Presentation_get_GrayLevelForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_GrayLevelForPrint.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_GrayLevelForPrint,self.Ptr)
        return ret

    @GrayLevelForPrint.setter
    def GrayLevelForPrint(self, value:bool):
        GetDllLibPpt().Presentation_set_GrayLevelForPrint.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_GrayLevelForPrint,self.Ptr, value)

    @property
    def IsNoteRetained(self)->bool:
        GetDllLibPpt().Presentation_get_IsNoteRetained.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_IsNoteRetained.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_IsNoteRetained,self.Ptr)
        return ret

    @IsNoteRetained.setter
    def IsNoteRetained(self, value:bool):
        GetDllLibPpt().Presentation_set_IsNoteRetained.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_IsNoteRetained,self.Ptr, value)



    def AddEmbeddedFont(self,pathName:str)->str:
        """
    <summary>
        
    </summary>
        """
        pathNamePtr = StrToPtr(pathName)
        GetDllLibPpt().Presentation_AddEmbeddedFont.argtypes=[c_void_p,c_char_p]
        GetDllLibPpt().Presentation_AddEmbeddedFont.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Presentation_AddEmbeddedFont,self.Ptr,pathNamePtr))
        return ret
    
    
    @staticmethod
    def SetDefaultFontName(value:str):
        """

        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Presentation_set_DefaultFontName.argtypes=[c_char_p]
        GetDllLibPpt().Presentation_set_DefaultFontName.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_set_DefaultFontName,valuePtr)

    @staticmethod   
    def ResetDefaultFontName():
        """

        """
        GetDllLibPpt().Presentation_Reset_DefaultFontName.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_Reset_DefaultFontName.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_Reset_DefaultFontName)

    @staticmethod
    def SetCustomFontsDirctory(value:str):
        """

        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Presentation_set_CustomFontsDirctory.argtypes=[c_char_p]
        GetDllLibPpt().Presentation_set_CustomFontsDirctory.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_set_CustomFontsDirctory,valuePtr)


    def ReplaceAndFormatText(self,value1:str,value2:str,format:DefaultTextRangeProperties):
        """

        """
        value1Ptr = StrToPtr(value1)
        value2Ptr = StrToPtr(value2)
        GetDllLibPpt().Presentation_ReplaceAndFormatText.argtypes=[c_void_p,c_char_p,c_char_p,c_void_p]
        GetDllLibPpt().Presentation_ReplaceAndFormatText.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_ReplaceAndFormatText,self.Ptr,value1Ptr,value2Ptr,format.Ptr)

