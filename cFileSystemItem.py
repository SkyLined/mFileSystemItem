import os, zipfile;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

from mNotProvided import *;
try:
  from mWindowsSDK.mKernel32 import oKernel32DLL as o0Kernel32DLL;
  from mWindowsSDK import LPCWSTR, FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_READONLY, DWORD;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mWindowsSDK'":
    raise;
  o0Kernel32DLL = None;

from .fs0GetDOSPath import fs0GetDOSPath;
from .fsGetNormalizedPath import fsGetNormalizedPath;
from .fsGetWindowsPath import fsGetWindowsPath;

gdsInvalidPathCharacterNormalTranslationMap = {
  # Translates characters that are not valid in file/folder names to a visually similar unicode character.
  '"':     "''",     # Double APOSTROPHY
  "<":     "[",      # LEFT SQUARE BRACKET
  ">":     "]",      # RIGHT SQUARE BRACKET
  "\\":    " ",      # SPACE
  "/":     " ",      # SPACE
  "?":     "!",      # EXCLAMATION MARK
  "*":     "x",      # LATIN SMALL LETTER X
  ":":     ".",      # FULL STOP
  "|":     "!",      # EXCLAMATION MARK
};
gdsInvalidPathCharacterUnicodeHomographTranslationMap = {
  # Translates characters that are not valid in file/folder names to a visually similar unicode character.
  '\x00':  " ",      # ,- Assume cp437
  '\x01':  "\u263A", # |
  '\x02':  "\u263B", # |
  '\x03':  "\u2665", # |
  '\x04':  "\u2666", # |
  '\x05':  "\u2663", # |
  '\x06':  "\u2660", # |
  '\x07':  "\u2022", # |
  '\x08':  "\u25D8", # |
  '\x09':  "\u25CB", # |
  '\x0A':  "\u25D9", # |
  '\x0B':  "\u2642", # |
  '\x0C':  "\u2640", # |
  '\x0D':  "\u266A", # |
  '\x0E':  "\u266B", # |
  '\x0F':  "\u263C", # |
  '\x10':  "\u25BA", # |
  '\x11':  "\u25C4", # |
  '\x12':  "\u2195", # |
  '\x13':  "\u203C", # |
  '\x14':  "\u00B6", # |
  '\x15':  "\u00A7", # |
  '\x16':  "\u25AC", # |
  '\x17':  "\u21A8", # |
  '\x18':  "\u2191", # |
  '\x19':  "\u2193", # |
  '\x1A':  "\u2192", # |
  '\x1B':  "\u2190", # |
  '\x1C':  "\u221F", # |
  '\x1D':  "\u2194", # |
  '\x1E':  "\u25B2", # |
  '\x1F':  "\u25BC", # `-
  '"':     "″", # DOUBLE PRIME
  "<":     "〈", # LEFT ANGLE BRACKET
  ">":     "〉", # RIGHT ANGLE BRACKET
  "\\":    "⧹", # BIG REVERSE SOLIDUS
  "/":     "⧸", # BIG SOLIDUS
  "?":     "❓", # BLACK QUESTION MARK ORNAMENT
  "*":     "✱", # HEAVY ASTERISK
  ":":     "։", # ARMENIAN FULL STOP
  "|":     "ǀ", # LATIN LETTER DENTAL CLICK
};
for uCharCode in range(0, 0x20):
  # Translate control codes
  gdsInvalidPathCharacterNormalTranslationMap[chr(uCharCode)] = "."; # FULL STOP

class cFileSystemItem(object):
  bSupportsZipFiles = True; # To allow code that may use this or another implementation to detect if .zip files are supported
  @staticmethod
  def fsGetValidName(sName, bUseUnicodeHomographs = True):
    # Convert a string with arbitrary characters (potentially including characters that are not valid in file system
    # items, such as ':' and '/') into a string that looks similar but does not contain any such invalid characters.
    # Be default similar looking Unicode characters are used as replacement where possible. This can be deisabled by
    # specifying `bUseUnicodeHomographs = False`.
    dsInvalidPathCharacterTranslationMap = gdsInvalidPathCharacterNormalTranslationMap if bUseUnicodeHomographs else \
                                           gdsInvalidPathCharacterUnicodeHomographTranslationMap;
    return "".join([
      (bUseUnicodeHomographs or ord(sChar) < 0x100) and dsInvalidPathCharacterTranslationMap.get(sChar, sChar) or "."
      for sChar in str(sName)
    ]);
  
  @ShowDebugOutput
  def __init__(oSelf, sPath = None, o0Parent = None):
    oSelf.sPath = fsGetNormalizedPath(sPath, o0Parent.sPath if o0Parent else None);
    if o0Parent:
      sParentPath = fsGetNormalizedPath(oSelf.sPath + os.sep + "..");
      assert sParentPath == o0Parent.sPath, \
          "Cannot create a child (path = %s, normalized = %s, parent = %s) for the given parent (path %s)" % \
          (repr(sPath), repr(oSelf.sPath), repr(sParentPath), repr(o0Parent.sPath));
    oSelf.sName = os.path.basename(oSelf.sPath);
    uDotIndex = oSelf.sName.rfind(".");
    oSelf.s0Extension = None if uDotIndex == -1 else oSelf.sName[uDotIndex + 1:];
    
    oSelf.__sWindowsPath = None;
    oSelf.__bWindowsPathSet = False;
    oSelf.__sDOSPath = None;
    oSelf.__bDOSPathSet = False;
    
    oSelf.__oRoot = o0Parent.oRoot if o0Parent else None;
    oSelf.__o0Parent = o0Parent;
    oSelf.__bParentSet = o0Parent is not None;
    oSelf.__o0PyFile = None;
    oSelf.__bPyFileIsInsideZipFile = False;
    oSelf.__o0PyZipFile = None;
    oSelf.__do0PyZipInfo_by_sZipInternalPath = {};
    oSelf.__doPyFile_by_sZipInternalPath = {};
    oSelf.__dbWritable_by_sZipInternalPath = {};
    oSelf.__bWritable = False;
    return;
  
  @property
  def o0Parent(oSelf):
    if not oSelf.__bParentSet:
      sParentPath = fsGetNormalizedPath(oSelf.sPath + os.sep + "..");
      # This will be None for root nodes, where sParentPath == its own path.
      oSelf.__o0Parent = oSelf.__class__(sParentPath) if sParentPath != oSelf.sPath else None;
      assert oSelf.__o0Parent is None or sParentPath == oSelf.__o0Parent.sPath, \
          "Cannot create a parent (path = %s, normalized = %s) for path %s: result is %s" % \
          (repr(oSelf.sPath + os.sep + ".."), repr(sParentPath), repr(oSelf.sPath), repr(oSelf.__o0Parent.sPath));
      oSelf.__bParentSet = True;
    return oSelf.__o0Parent;
  
  @property
  def oRoot(oSelf):
    if not oSelf.__oRoot:
      oSelf.__oRoot = oSelf.o0Parent.oRoot if oSelf.o0Parent else oSelf;
    return oSelf.__oRoot;
  
  @ShowDebugOutput
  def fbIsInsideZipFile(oSelf, bThrowErrors = False):
    return oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) is not None;
  
  @ShowDebugOutput
  def fo0GetZipRoot(oSelf, bThrowErrors = False):
    o0Ancestor = oSelf.o0Parent;
    # Check the parent and subsequent ancestors to see if they are valid zip files:
    while o0Ancestor:
      if o0Ancestor.fbIsValidZipFile(bParseZipFiles = True, bThrowErrors = bThrowErrors):
        # If its parent is a valid zip file, this is its zip root
        return o0Ancestor;
      if os.path.exists(o0Ancestor.sWindowsPath):
        fShowDebugOutput("ancestor %s exists on the file system but is not a valid zip file" % o0Ancestor.sPath);
        return None;
      o0Ancestor = o0Ancestor.o0Parent;
    # This item has no parent that is a valid zip file.
    fShowDebugOutput("none of the ancestors are valid zip files");
    return None;
  
  def __del__(oSelf):
    if oSelf.__o0PyZipFile:
      try:
        oSelf.__o0PyZipFile.close();
      except Exception:
        pass;
    if oSelf.__o0PyFile:
      try:
        oSelf.__o0PyFile.close();
      except Exception:
        pass;
      oSelf.__o0PyFile = None;
      oSelf.__fReapplyAccessLimitingAttributesAfterOperation();
    try:
      asZipFileOpenWritableInternalPaths = list(oSelf.__dbWritable_by_sZipInternalPath.keys());
    except Exception:
      pass;
    else:
      assert len(asZipFileOpenWritableInternalPaths) == 0, \
          "cFileSystemItem: Zip file %s was destroyed while the following writable files were still open: %s" % \
          (oSelf.sPath, ", ".join([
            sZipInternalPath.replace("/", os.sep)
            for sZipInternalPath in asZipFileOpenWritableInternalPaths
          ]));
  
  def __fRemoveAccessLimitingAttributesBeforeOperation(oSelf):
    if o0Kernel32DLL:
      uFlags = o0Kernel32DLL.GetFileAttributesW(LPCWSTR(oSelf.sWindowsPath)).fuGetValue();
      oSelf.__bWasHiddenBeforeOpen = (uFlags & FILE_ATTRIBUTE_HIDDEN) != 0;
      if oSelf.__bWasHiddenBeforeOpen:
        uFlags -= FILE_ATTRIBUTE_HIDDEN;
      oSelf.__bWasReadOnlyBeforeOpen = (uFlags & FILE_ATTRIBUTE_READONLY) != 0;
      if oSelf.__bWasReadOnlyBeforeOpen:
        uFlags -= FILE_ATTRIBUTE_READONLY;
      if oSelf.__bWasHiddenBeforeOpen or oSelf.__bWasReadOnlyBeforeOpen:
        o0Kernel32DLL.SetFileAttributesW(LPCWSTR(oSelf.sWindowsPath), DWORD(uFlags));
  
  def __fReapplyAccessLimitingAttributesAfterOperation(oSelf):
    if o0Kernel32DLL and (oSelf.__bWasHiddenBeforeOpen or oSelf.__bWasReadOnlyBeforeOpen):
      uFlags = o0Kernel32DLL.GetFileAttributesW(LPCWSTR(oSelf.sWindowsPath)).fuGetValue();
      if oSelf.__bWasHiddenBeforeOpen:
        uFlags |= FILE_ATTRIBUTE_HIDDEN;
      if oSelf.__bWasReadOnlyBeforeOpen:
        uFlags |= FILE_ATTRIBUTE_READONLY;
      o0Kernel32DLL.SetFileAttributesW(LPCWSTR(oSelf.sWindowsPath), DWORD(uFlags));
  
  @ShowDebugOutput
  def fsGetRelativePathTo(oSelf, sAbsoluteDescendantPath_or_oDescendant, bThrowErrors = False):
    if isinstance(sAbsoluteDescendantPath_or_oDescendant, cFileSystemItem):
      sAbsoluteDescendantPath = sAbsoluteDescendantPath_or_oDescendant.sPath;
    else:
      sAbsoluteDescendantPath = sAbsoluteDescendantPath_or_oDescendant;
    if (
      not sAbsoluteDescendantPath.startswith(oSelf.sPath)
      or sAbsoluteDescendantPath[len(oSelf.sPath):len(oSelf.sPath) + 1] not in [os.sep, os.altsep]
    ):
      assert not bThrowErrors, \
          "Cannot get relative path for %s as it is not a descendant of %s" % (sAbsoluteDescendantPath, oSelf.sPath);
      return None;
    sRelativePath = sAbsoluteDescendantPath[len(oSelf.sPath) + 1:];
    return sRelativePath;
  
  @property
  def sWindowsPath(oSelf):
    if not oSelf.__bWindowsPathSet:
      oSelf.__sWindowsPath = fsGetWindowsPath(oSelf.sPath);
      oSelf.__bWindowsPathSet = True;
    return oSelf.__sWindowsPath;
  
  @property
  def s0DOSPath(oSelf):
    if not oSelf.__bDOSPathSet:
      if not oSelf.fbIsInsideZipFile(bThrowErrors = False):
        oSelf.__sDOSPath = fs0GetDOSPath(oSelf.sPath);
      oSelf.__bDOSPathSet = True;
    return oSelf.__sDOSPath;
  
  @ShowDebugOutput
  def fuGetSize(oSelf, bParseZipFiles = False):
    return oSelf.__fu0GetSize(bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fu0GetSize(oSelf, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fu0GetSize(bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fu0GetSize \
      import cFileSystemItem_fu0GetSize \
      as __fu0GetSize;
  
  @ShowDebugOutput
  def fuGetCompressedSize(oSelf):
    return oSelf.__fu0GetCompressedSize(bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fu0GetCompressedSize(oSelf, bThrowErrors = False):
    return oSelf.__fu0GetCompressedSize(bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fu0GetCompressedSize \
      import cFileSystemItem_fu0GetCompressedSize \
      as __fu0GetCompressedSize;
  
  @ShowDebugOutput
  def fbExists(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a zip file");
      return True;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a file");
      return True;
    try:
      if os.path.exists(oSelf.sWindowsPath):
        fShowDebugOutput("found on the file system");
        return True;
    except:
      if bThrowErrors:
        raise;
    if not bParseZipFiles:
      fShowDebugOutput("not found on the file system");
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
    if o0ZipRoot and o0ZipRoot.__fbZipFileContainsDescendant(oSelf.sPath, bThrowErrors):
      fShowDebugOutput("found inside zip file %s" % o0ZipRoot.sPath);
      return True;
    fShowDebugOutput("not found on the file system or inside a zip file");
    return False;
  
  @ShowDebugOutput
  def fbIsFolder(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a zip file");
      return False;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a file");
      return False;
    try:
      if os.path.isdir(oSelf.sWindowsPath):
        fShowDebugOutput("found as a folder on the file system");
        return True;
    except:
      if bThrowErrors:
        raise;
    if not bParseZipFiles:
      fShowDebugOutput("not found on the file system");
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
    if o0ZipRoot and o0ZipRoot.__fbZipFileContainsDescendantFolder(oSelf.sPath, bThrowErrors):
      fShowDebugOutput("found as a folder inside zip file %s" % o0ZipRoot.sPath);
      return True;
    fShowDebugOutput("not found on the file system or inside a zip file");
    return False;
  
  @ShowDebugOutput
  def fbIsFile(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a zip file");
      return True;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a file");
      return True;
    try:
      if os.path.isfile(oSelf.sWindowsPath):
        fShowDebugOutput("found as a file on the file system");
        return True;
    except:
      if bThrowErrors:
        raise;
    if not bParseZipFiles:
      fShowDebugOutput("not found on the file system");
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
    if o0ZipRoot and o0ZipRoot.__fbZipFileContainsDescendantFile(oSelf.sPath, bThrowErrors):
      fShowDebugOutput("found as a file inside zip file %s" % o0ZipRoot.sPath);
      return True;
    fShowDebugOutput("was not found on the file system or inside a zip file");
    return False;
  
  @ShowDebugOutput
  def fbIsValidZipFile(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a zip file");
      return True;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("is open as a file");
      return False;
    # If the file exists, try to parse the .zip file to make sure it is valid
    try:
      if os.path.isfile(oSelf.sWindowsPath):
        try:
          zipfile.ZipFile(oSelf.sWindowsPath, "r").close();
        except (IOError, zipfile.BadZipfile) as oError:
          fShowDebugOutput("found on the file system but it is not a valid zip file");
          return False;
        else:
          fShowDebugOutput("found on the file system and is a valid zip file");
          return True;
    except:
      if bThrowErrors:
        raise;
    if not bParseZipFiles:
      fShowDebugOutput("not found on the file system");
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
    if not o0ZipRoot:
      fShowDebugOutput("not found on the file system or inside a zip file");
      return False;
    o0PyFile = o0ZipRoot.__fo0OpenZipFileDescendantAsPyFile(oSelf.sPath, bWritable = False, bThrowErrors = bThrowErrors);
    if not oPyFile:
      fShowDebugOutput("could not be opened inside zip file %s" % o0ZipRoot.sPath);
      return False;
    try:
      zipfile.ZipFile(oPyFile, "r").close();
    except zipfile.BadZipfile:
      fShowDebugOutput("found inside zip file %s but is not a valid zip file itself" % o0ZipRoot.sPath);
      return False;
    finally:
      # This should always succeed, so we always throw errors if it does not.
      o0ZipRoot.__fbCloseZipFileDescendantPyFile(oSelf.sPath, oPyFile, bThrowErrors = True);
    fShowDebugOutput("found inside zip file %s and is a valid zip file itself" % o0ZipRoot.sPath);
    return True;
  
  def foMustBeFile(oSelf):
    assert oSelf.fbIsFile(), \
        "%s is not a file" % oSelf.sPath;
    return oSelf;
  def foMustBeFolder(oSelf):
    assert oSelf.fbIsFolder(), \
        "%s is not a folder" % oSelf.sPath;
    return oSelf;
  def foMustBeValidZipFile(oSelf):
    assert oSelf.fbIsValidzipFile(), \
        "%s is not a valid zip file" % oSelf.sPath;
    return oSelf;
  
  @ShowDebugOutput
  def fCreateAsFolder(oSelf, bCreateParents = False, bParseZipFiles = False):
    assert oSelf.__fbCreateAsFolder(bCreateParents, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbCreateAsFolder(oSelf, bCreateParents = False, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fbCreateAsFolder(bCreateParents, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbCreateAsFolder \
      import cFileSystemItem_fbCreateAsFolder \
      as __fbCreateAsFolder;
  
  @ShowDebugOutput
  def faoGetChildren(oSelf, bParseZipFiles = False):
    return oSelf.__fa0oGetChildren(bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fa0oGetChildren(oSelf, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fa0oGetChildren(bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fa0oGetChildren \
      import cFileSystemItem_fa0oGetChildren \
      as __fa0oGetChildren;
  
  @ShowDebugOutput
  def foGetChild(oSelf, sChildName, bParseZipFiles = False, bFixCase = False):
    return oSelf.__fo0GetChild(sChildName, bParseZipFiles, bFixCase, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fo0GetChild(oSelf, sChildName, bParseZipFiles = False, bFixCase = False, bThrowErrors = False):
    return oSelf.__fo0GetChild(sChildName, bParseZipFiles, bFixCase, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fo0GetChild \
      import cFileSystemItem_fo0GetChild \
      as __fo0GetChild;
  
  @ShowDebugOutput
  def faoGetDescendants(oSelf, bParseZipFiles = False, bParseDescendantZipFiles = False):
    return oSelf.__fa0oGetDescendants(bParseZipFiles, bParseDescendantZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fa0oGetDescendants(oSelf, bParseZipFiles = False, bParseDescendantZipFiles = False, bThrowErrors = False):
    return oSelf.__fa0oGetDescendants(bParseZipFiles, bParseDescendantZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fa0oGetDescendants \
      import cFileSystemItem_fa0oGetDescendants \
      as __fa0oGetDescendants;
  
  @ShowDebugOutput
  def foGetDescendant(oSelf, sDescendantRelativePath, bFixCase = False, bParseZipFiles = False):
    return oSelf.__fo0GetDescendant(sDescendantRelativePath, bFixCase, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fo0GetDescendant(oSelf, sDescendantRelativePath, bFixCase = False, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fo0GetDescendant(sDescendantRelativePath, bFixCase, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fo0GetDescendant \
      import cFileSystemItem_fo0GetDescendant \
      as __fo0GetDescendant;
  
  @ShowDebugOutput
  def fSetAsCurrentWorkingDirectory(oSelf):
    assert oSelf.__fbSetAsCurrentWorkingDirectory(bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbSetAsCurrentWorkingDirectory(oSelf, bThrowErrors = False):
    return oSelf.__fbSetAsCurrentWorkingDirectory(bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbSetAsCurrentWorkingDirectory \
      import cFileSystemItem_fbSetAsCurrentWorkingDirectory \
      as __fbSetAsCurrentWorkingDirectory;
  
  @ShowDebugOutput
  def fCreateAsFile(oSelf, sbData = b"", bCreateParents = False, bParseZipFiles = False, bKeepOpen = False):
    fAssertType("sbData", sbData, bytes);
    assert oSelf.__fbCreateAsFile(sbData, bCreateParents, bParseZipFiles, bKeepOpen, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbCreateAsFile(oSelf, sbData = b"", bCreateParents = False, bParseZipFiles = False, bKeepOpen = False, bThrowErrors = False):
    fAssertType("sbData", sbData, bytes);
    return oSelf.__fbCreateAsFile(sbData, bCreateParents, bParseZipFiles, bKeepOpen, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbCreateAsFile \
      import cFileSystemItem_fbCreateAsFile \
      as __fbCreateAsFile;
  
  @ShowDebugOutput
  def fOpenAsFile(oSelf, bWritable = False, bAppend = False, bParseZipFiles = False):
    assert oSelf.__fbOpenAsFile(bWritable, bAppend, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbOpenAsFile(oSelf, bWritable = False, bAppend = False, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fbOpenAsFile(bWritable, bAppend, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbOpenAsFile \
    import cFileSystemItem_fbOpenAsFile \
    as __fbOpenAsFile;
  
  @ShowDebugOutput
  def fsbRead(oSelf, bKeepOpen = None, bParseZipFiles = True):
    return oSelf.__fsb0Read(bKeepOpen, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fsb0Read(oSelf, bKeepOpen = None, bParseZipFiles = True, bThrowErrors = False):
    return oSelf.__fsb0Read(bKeepOpen, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fsb0Read \
      import cFileSystemItem_fsb0Read \
      as __fsb0Read;
  
  @ShowDebugOutput
  def fWrite(oSelf, sbData, bAppend = False, bCreateParents = False, bKeepOpen = None, bParseZipFiles = True):
    fAssertType("sbData", sbData, bytes);
    assert oSelf.__fbWrite(sbData, bAppend, bCreateParents, bKeepOpen, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbWrite(oSelf, sbData, bAppend = False, bCreateParents = False, bKeepOpen = None, bParseZipFiles = True, bThrowErrors = False):
    fAssertType("sbData", sbData, bytes);
    return oSelf.__fbWrite(sbData, bAppend, bCreateParents, bKeepOpen, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbWrite \
      import cFileSystemItem_fbWrite \
      as __fbWrite;
    
  @ShowDebugOutput
  def fCreateAsZipFile(oSelf, bKeepOpen = False, bCreateParents = False, bParseZipFiles = False):
    assert oSelf.__fbCreateAsZipFile(bKeepOpen, bCreateParents, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbCreateAsZipFile( oSelf, bKeepOpen = False, bCreateParents = False, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fbCreateAsZipFile(bKeepOpen, bCreateParents, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbCreateAsZipFile \
      import cFileSystemItem_fbCreateAsZipFile \
      as __fbCreateAsZipFile;
  
  @ShowDebugOutput
  def fOpenAsZipFile(oSelf, bWritable = False, bParseZipFiles = False, bThrowErrors = False):
    assert oSelf.__fbOpenAsZipFile(bWritable, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbOpenAsZipFile(oSelf, bWritable = False, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fbOpenAsZipFile(bWritable, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbOpenAsZipFile \
      import cFileSystemItem_fbOpenAsZipFile \
      as __fbOpenAsZipFile;
  
  @ShowDebugOutput
  def fCreateAsParent(oSelf, bParseZipFiles = False):
    assert oSelf.__fbCreateAsParent(bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbCreateAsParent(oSelf, bParseZipFiles = False, bThrowErrors = False):
    return oSelf.__fbCreateAsParent(bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbCreateAsParent \
      import cFileSystemItem_fbCreateAsParent \
      as __fbCreateAsParent;
    
  def fbIsOpenAsFile(oSelf, bThrowErrors = False):
    return oSelf.__o0PyFile is not None and not oSelf.__o0PyZipFile is not None;
  def fbIsOpenAsZipFile(oSelf, bThrowErrors = False):
    return oSelf.__o0PyZipFile is not None;
  def fbIsOpen(oSelf, bThrowErrors = False):
    return oSelf.__o0PyFile is not None;
  
  @ShowDebugOutput
  def fClose(oSelf):
    assert oSelf.__fbClose(bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbClose(oSelf, bThrowErrors = False):
    return oSelf.__fbClose(bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbClose \
      import cFileSystemItem_fbClose \
      as __fbClose;
  
  @ShowDebugOutput
  def fRename(oSelf, sNewName, bParseZipFiles = True):
    assert oSelf.__fbRename(sNewName, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbRename(oSelf, sNewName, bParseZipFiles = True, bThrowErrors = False):
    return oSelf.__fbRename(sNewName, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbRename \
      import cFileSystemItem_fbRename \
      as __fbRename;
  
  @ShowDebugOutput
  def fMove(oSelf, oNewItem, bParseZipFiles = True):
    assert oSelf.__fbMove(oNewItem, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbMove(oSelf, oNewItem, bParseZipFiles = True, bThrowErrors = False):
    return oSelf.__fbMove(oNewItem, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbMove \
      import cFileSystemItem_fbMove \
      as __fbMove;
  
  @ShowDebugOutput
  def fDeleteDescendants(oSelf, bClose = False, bParseZipFiles = True):
    assert oSelf.__fbDeleteDescendants(bClose, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbDeleteDescendants(oSelf, bClose = False, bParseZipFiles = True, bThrowErrors = False):
    return oSelf.__fbDeleteDescendants(bClose, bParseZipFile, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbDeleteDescendants \
      import cFileSystemItem_fbDeleteDescendants \
      as __fbDeleteDescendants;
  
  @ShowDebugOutput
  def fDelete(oSelf, bClose = False, bParseZipFiles = True):
    assert oSelf.__fbDelete(bClose, bParseZipFiles, bThrowErrors = True, bSanityChecks = True);
  @ShowDebugOutput
  def fbDelete(oSelf, bClose = False, bParseZipFiles = True, bThrowErrors = False):
    return oSelf.__fbDelete(bClose, bParseZipFiles, bThrowErrors, bSanityChecks = True);
  from .cFileSystemItem_fbDelete \
      import cFileSystemItem_fbDelete \
      as __fbDelete;
  
  from .cFileSystemItem_fdoGetCachedPyZipInfo_by_sZipInternalPath \
      import cFileSystemItem_fdoGetCachedPyZipInfo_by_sZipInternalPath \
      as __fdoGetCachedPyZipInfo_by_sZipInternalPath;
  from .cFileSystemItem_fbZipFileContainsDescendant \
      import cFileSystemItem_fbZipFileContainsDescendant \
      as __fbZipFileContainsDescendant;
  from .cFileSystemItem_fbZipFileContainsDescendantFolder \
      import cFileSystemItem_fbZipFileContainsDescendantFolder \
      as __fbZipFileContainsDescendantFolder;
  from .cFileSystemItem_fbZipFileContainsDescendantFile \
      import cFileSystemItem_fbZipFileContainsDescendantFile \
      as __fbZipFileContainsDescendantFile;
  from .cFileSystemItem_fo0CreateZipFileDescendant \
      import cFileSystemItem_fo0CreateZipFileDescendant \
      as __fo0CreateZipFileDescendant;
  from .cFileSystemItem_fo0OpenZipFileDescendantAsPyFile \
      import cFileSystemItem_fo0OpenZipFileDescendantAsPyFile \
      as __fo0OpenZipFileDescendantAsPyFile;
  from .cFileSystemItem_fbCloseZipFileDescendantPyFile \
      import cFileSystemItem_fbCloseZipFileDescendantPyFile \
      as __fbCloseZipFileDescendantPyFile;
  from .cFileSystemItem_fasGetChildNamesOfZipFileDescendant \
      import cFileSystemItem_fasGetChildNamesOfZipFileDescendant \
      as __fasGetChildNamesOfZipFileDescendant;
  from .cFileSystemItem_fu0GetSizeOfZipFileDescendant \
      import cFileSystemItem_fu0GetSizeOfZipFileDescendant \
      as __fu0GetSizeOfZipFileDescendant;
  from .cFileSystemItem_fu0GetCompressedSizeOfZipFileDescendant \
      import cFileSystemItem_fu0GetCompressedSizeOfZipFileDescendant \
      as __fu0GetCompressedSizeOfZipFileDescendant;
  from .cFileSystemItem_fo0GetZipInfoForZipFileDescendant \
      import cFileSystemItem_fo0GetZipInfoForZipFileDescendant \
      as __fo0GetZipInfoForZipFileDescendant;

  def __repr__(oSelf):
    return "<%s %s #%d>" % (oSelf.__class__.__name__, oSelf, id(oSelf));
  def fsToString(oSelf):
    return "%s{%s#%d}" % (oSelf.__class__.__name__, oSelf.sPath, id(oSelf));
  def __str__(oSelf):
    return oSelf.sPath;