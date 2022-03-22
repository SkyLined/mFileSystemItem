import os;

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

from ..fs0GetDOSPath import fs0GetDOSPath;
from ..fsGetNormalizedPath import fsGetNormalizedPath;
from ..fsGetWindowsPath import fsGetWindowsPath;

gdsInvalidPathCharacterNormalTranslationMap = {
  # Translates characters that are not valid in file/folder names to a visually similar unicode character.
  '\x00':  ".",      #
  '\x01':  ".",      #
  '\x02':  ".",      #
  '\x03':  ".",      #
  '\x04':  ".",      #
  '\x05':  ".",      #
  '\x06':  ".",      #
  '\x07':  ".",      #
  '\x08':  ".",      #
  '\x09':  ".",      #
  '\x0A':  ".",      #
  '\x0B':  ".",      #
  '\x0C':  ".",      #
  '\x0D':  ".",      #
  '\x0E':  ".",      #
  '\x0F':  ".",      #
  '\x10':  ".",      #
  '\x11':  ".",      #
  '\x12':  ".",      #
  '\x13':  ".",      #
  '\x14':  ".",      #
  '\x15':  ".",      #
  '\x16':  ".",      #
  '\x17':  ".",      #
  '\x18':  ".",      #
  '\x19':  ".",      #
  '\x1A':  ".",      #
  '\x1B':  ".",      #
  '\x1C':  ".",      #
  '\x1D':  ".",      #
  '\x1E':  ".",      #
  '\x1F':  ".",      #
  '"':     "''",     # Double APOSTROPHY
  "<":     "[",      # LEFT SQUARE BRACKET
  ">":     "]",      # RIGHT SQUARE BRACKET
  "\\":    ".",      # FULL STOP
  "/":     ".",      # FULL STOP
  "?":     ".",      # FULL STOP
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
  bSupportsZipFiles = False; # Allow code to detect if .zip files are supported
  @staticmethod
  def fsGetValidName(sName, bUseUnicodeHomographs = True):
    # Convert a string with arbitrary characters (potentially including characters that are not valid in file system
    # items, such as ':' and '/') into a string that looks similar but does not contain any such invalid characters.
    # Be default similar looking Unicode characters are used as replacement where possible. This can be deisabled by
    # specifying `bUseUnicodeHomographs = False`.
    if bUseUnicodeHomographs:
      return "".join([
        gdsInvalidPathCharacterUnicodeHomographTranslationMap.get(sChar, sChar) \
        for sChar in sName
      ]);      
    return "".join([
      gdsInvalidPathCharacterNormalTranslationMap.get(sChar, sChar) if ord(sChar) < 0x100 else "."
      for sChar in sName
    ]);
  @classmethod
  def fbIsValidPath(cClass, sPath):
    if os.altsep:
      sPath = sPath.replace(os.altsep, os.sep);
    if sPath.startswith("\\\\?\\"):
      sPath = sPath[4:];
      asComponents = sPath.split(os.sep);
      sDrive = asComponents.pop(0);
      if len(sDrive) != 2 or "a" > sDrive[0].lower() > "z" or sDrive[-1] != ":":
        return False;
    else:
      asComponents = sPath.split(os.sep);
      if asComponents[0][-1:] == ":":
        sDrive = asComponents.pop(0);
        if len(sDrive) != 2 or "a" > sDrive[0].lower() > "z":
          return False;
    for sName in asComponents:
      if not cClass.fbIsValidName(sName):
        return False;
    return True;
  @staticmethod
  def fbIsValidName(sName):
    # The translation maps list the characters that are not valid:
    for sChar in sName:
      if sChar in gdsInvalidPathCharacterUnicodeHomographTranslationMap:
        return False;
    return True;
  
  @ShowDebugOutput
  def __init__(oSelf, sPath, oz0Parent = zNotProvided):
    assert oSelf.fbIsValidPath(sPath), \
        "%s is not a valid file system item path" % sPath;
    if fbIsProvided(oz0Parent):
      oSelf.sPath = fsGetNormalizedPath(sPath, sBasePath = oz0Parent.sPath if oz0Parent else None);
      if oz0Parent is not None:
        sParentPath = fsGetNormalizedPath(oSelf.sPath + os.sep + "..");
        assert sParentPath == oz0Parent.sPath, \
            "Cannot create a child (path = %s, normalized = %s, parent = %s) for the given parent (path %s)" % \
            (repr(sPath), repr(oSelf.sPath), repr(sParentPath), repr(oz0Parent.sPath));
      oSelf.__bParentSet = True;
      oSelf.__o0Parent = oz0Parent;
      oSelf.__bRootSet = True;
      oSelf.__oRoot = oz0Parent.oRoot if oz0Parent else oSelf;
    else:
      oSelf.sPath = fsGetNormalizedPath(sPath);
      oSelf.__bParentSet = False;
      oSelf.__bRootSet = False;
    oSelf.sName = os.path.basename(oSelf.sPath);
    uDotIndex = oSelf.sName.rfind(".");
    oSelf.s0Extension = None if uDotIndex == -1 else oSelf.sName[uDotIndex + 1:];
    
    oSelf.__sWindowsPath = None;
    oSelf.__bWindowsPathSet = False;
    oSelf.__sDOSPath = None;
    oSelf.__bDOSPathSet = False;
    
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
    if not oSelf.__bRootSet:
      oSelf.__oRoot = oSelf.o0Parent.oRoot if oSelf.o0Parent else oSelf;
    return oSelf.__oRoot;
  
  def __fRemoveAccessLimitingAttributesBeforeOperation(oSelf, bMustBeWritable = False):
    if o0Kernel32DLL:
      uFlags = o0Kernel32DLL.GetFileAttributesW(LPCWSTR(oSelf.sWindowsPath)).fuGetValue();
      oSelf.__bWasHiddenBeforeOpen = (uFlags & FILE_ATTRIBUTE_HIDDEN) != 0;
      if oSelf.__bWasHiddenBeforeOpen:
        uFlags -= FILE_ATTRIBUTE_HIDDEN;
      oSelf.__bWasReadOnlyBeforeOpen = (uFlags & FILE_ATTRIBUTE_READONLY) != 0;
      if oSelf.__bWasReadOnlyBeforeOpen and bMustBeWritable:
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
      oSelf.__sDOSPath = fs0GetDOSPath(oSelf.sPath);
      oSelf.__bDOSPathSet = True;
    return oSelf.__sDOSPath;
  
  @ShowDebugOutput
  def fuGetSize(oSelf):
    return oSelf.__fu0GetSize(bThrowErrors = True);
  @ShowDebugOutput
  def fu0GetSize(oSelf, bThrowErrors = False):
    return oSelf.__fu0GetSize(bThrowErrors);
  from .cFileSystemItem_fu0GetSize \
      import cFileSystemItem_fu0GetSize \
      as __fu0GetSize;
  
  @ShowDebugOutput
  def fbExists(oSelf, bThrowErrors = False):
    try:
      if os.path.exists(oSelf.sWindowsPath):
        fShowDebugOutput("found on the file system");
        return True;
    except:
      if bThrowErrors:
        raise;
    fShowDebugOutput("not found on the file system");
    return False;
  
  @ShowDebugOutput
  def fbIsFolder(oSelf, bThrowErrors = False):
    try:
      if os.path.isdir(oSelf.sWindowsPath):
        fShowDebugOutput("found as a folder on the file system");
        return True;
    except:
      if bThrowErrors:
        raise;
  
  @ShowDebugOutput
  def fbIsFile(oSelf, bThrowErrors = False):
    try:
      if os.path.isfile(oSelf.sWindowsPath):
        fShowDebugOutput("found as a file on the file system");
        return True;
    except:
      if bThrowErrors:
        raise;
    fShowDebugOutput("not found on the file system");
    return False;
  
  def foMustBeFile(oSelf):
    assert oSelf.fbIsFile(), \
        "%s is not a file" % oSelf.sPath;
    return oSelf;
  def foMustBeFolder(oSelf):
    assert oSelf.fbIsFolder(), \
        "%s is not a folder" % oSelf.sPath;
    return oSelf;
  
  @ShowDebugOutput
  def fCreateAsFolder(oSelf, bCreateParents = False):
    assert oSelf.__fbCreateAsFolder(bCreateParents, bThrowErrors = True);
  @ShowDebugOutput
  def fbCreateAsFolder(oSelf, bCreateParents = False, bThrowErrors = False):
    return oSelf.__fbCreateAsFolder(bCreateParents, bThrowErrors);
  from .cFileSystemItem_fbCreateAsFolder \
      import cFileSystemItem_fbCreateAsFolder \
      as __fbCreateAsFolder;
  
  @ShowDebugOutput
  def fCreateAsParent(oSelf):
    assert oSelf.__fbCreateAsParent(bCreateParents = True, bThrowErrors = True);
  @ShowDebugOutput
  def fbCreateAsParent(oSelf, bThrowErrors = False):
    return oSelf.__fbCreateAsFolder(bCreateParents = True, bThrowErrors = bThrowErrors);
  
  @ShowDebugOutput
  def faoGetChildren(oSelf):
    return oSelf.__fa0oGetChildren(bThrowErrors = True);
  @ShowDebugOutput
  def fa0oGetChildren(oSelf, bThrowErrors = False):
    return oSelf.__fa0oGetChildren(bThrowErrors);
  from .cFileSystemItem_fa0oGetChildren \
      import cFileSystemItem_fa0oGetChildren \
      as __fa0oGetChildren;
  
  @ShowDebugOutput
  def foGetChild(oSelf, sChildName, bFixCase = False):
    return oSelf.__fo0GetChild(sChildName, bFixCase, bThrowErrors = True);
  @ShowDebugOutput
  def fo0GetChild(oSelf, sChildName, bFixCase = False, bThrowErrors = False):
    return oSelf.__fo0GetChild(sChildName, bFixCase, bThrowErrors);
  from .cFileSystemItem_fo0GetChild \
      import cFileSystemItem_fo0GetChild \
      as __fo0GetChild;
  
  @ShowDebugOutput
  def faoGetDescendants(oSelf):
    return oSelf.__fa0oGetDescendants(bThrowErrors = True);
  @ShowDebugOutput
  def fa0oGetDescendants(oSelf, bThrowErrors = False):
    return oSelf.__fa0oGetDescendants(bThrowErrors);
  from .cFileSystemItem_fa0oGetDescendants \
      import cFileSystemItem_fa0oGetDescendants \
      as __fa0oGetDescendants;
  
  @ShowDebugOutput
  def foGetDescendant(oSelf, sDescendantRelativePath, bFixCase = False):
    return oSelf.__fo0GetDescendant(sDescendantRelativePath, bFixCase, bThrowErrors = True);
  @ShowDebugOutput
  def fo0GetDescendant(oSelf, sDescendantRelativePath, bFixCase = False, bThrowErrors = False):
    return oSelf.__fo0GetDescendant(sDescendantRelativePath, bFixCase, bThrowErrors);
  from .cFileSystemItem_fo0GetDescendant \
      import cFileSystemItem_fo0GetDescendant \
      as __fo0GetDescendant;
  
  @ShowDebugOutput
  def fSetAsCurrentWorkingDirectory(oSelf):
    assert oSelf.__fbSetAsCurrentWorkingDirectory(bThrowErrors = True);
  @ShowDebugOutput
  def fbSetAsCurrentWorkingDirectory(oSelf, bThrowErrors = False):
    return oSelf.__fbSetAsCurrentWorkingDirectory(bThrowErrors);
  from .cFileSystemItem_fbSetAsCurrentWorkingDirectory \
      import cFileSystemItem_fbSetAsCurrentWorkingDirectory \
      as __fbSetAsCurrentWorkingDirectory;
  
  @ShowDebugOutput
  def fCreateAsFile(oSelf, sbData = b"", bCreateParents = False):
    fAssertType("sbData", sbData, bytes);
    assert oSelf.__fbCreateAsFile(sbData, bCreateParents, bThrowErrors = True);
  @ShowDebugOutput
  def fbCreateAsFile(oSelf, sbData = b"", bCreateParents = False, bThrowErrors = False):
    fAssertType("sbData", sbData, bytes);
    return oSelf.__fbCreateAsFile(sbData, bCreateParents, bThrowErrors);
  from .cFileSystemItem_fbCreateAsFile \
      import cFileSystemItem_fbCreateAsFile \
      as __fbCreateAsFile;
  
  @ShowDebugOutput
  def fsbRead(oSelf):
    return oSelf.__fsb0Read(bThrowErrors = True);
  @ShowDebugOutput
  def fsb0Read(oSelf, bThrowErrors = False):
    return oSelf.__fsb0Read(bThrowErrors);
  from .cFileSystemItem_fsb0Read \
      import cFileSystemItem_fsb0Read \
      as __fsb0Read;
  
  @ShowDebugOutput
  def fWrite(oSelf, sbData, bAppend = False, bCreateParents = False):
    fAssertType("sbData", sbData, bytes);
    assert oSelf.__fbWrite(sbData, bAppend, bCreateParents, bThrowErrors = True);
  @ShowDebugOutput
  def fbWrite(oSelf, sbData, bAppend = False, bCreateParents = False, bThrowErrors = False):
    fAssertType("sbData", sbData, bytes);
    return oSelf.__fbWrite(sbData, bAppend, bCreateParents, bThrowErrors);
  from .cFileSystemItem_fbWrite \
      import cFileSystemItem_fbWrite \
      as __fbWrite;
  
  @ShowDebugOutput
  def foOpen(oSelf, bWritable = False, bAppend = False):
    return oSelf.__fo0Open(bWritable, bAppend, bThrowErrors = True);
  @ShowDebugOutput
  def fo0Open(oSelf, bWritable = False, bAppend = False, bThrowErrors = False):
    return oSelf.__fo0Open(bWritable, bAppend, bThrowErrors);
  from .cFileSystemItem_fo0Open \
      import cFileSystemItem_fo0Open \
      as __fo0Open;
  
  @ShowDebugOutput
  def fClose(oSelf, oPyFile):
    assert oSelf.__fbClose(oPyFile, bThrowErrors = True);
  @ShowDebugOutput
  def fbClose(oSelf, bWritable = False, bAppend = False, bThrowErrors = False):
    return oSelf.__fbClose(oPyFile, bThrowErrors = bThrowErrors);
  from .cFileSystemItem_fbClose \
      import cFileSystemItem_fbClose \
      as __fbClose;
  
  @ShowDebugOutput
  def fRename(oSelf, sNewName):
    assert oSelf.__fbRename(sNewName, bThrowErrors = True);
  @ShowDebugOutput
  def fbRename(oSelf, sNewName, bThrowErrors = False):
    return oSelf.__fbRename(sNewName, bThrowErrors);
  from .cFileSystemItem_fbRename \
      import cFileSystemItem_fbRename \
      as __fbRename;
  
  @ShowDebugOutput
  def fMove(oSelf, oNewItem):
    assert oSelf.__fbMove(oNewItem, bThrowErrors = True);
  @ShowDebugOutput
  def fbMove(oSelf, oNewItem, bThrowErrors = False):
    return oSelf.__fbMove(oNewItem, bThrowErrors);
  from .cFileSystemItem_fbMove \
      import cFileSystemItem_fbMove \
      as __fbMove;
  
  @ShowDebugOutput
  def fDeleteDescendants(oSelf):
    assert oSelf.__fbDeleteDescendants(bThrowErrors = True);
  @ShowDebugOutput
  def fbDeleteDescendants(oSelf, bThrowErrors = False):
    return oSelf.__fbDeleteDescendants(bThrowErrors);
  from .cFileSystemItem_fbDeleteDescendants \
      import cFileSystemItem_fbDeleteDescendants \
      as __fbDeleteDescendants;
  
  @ShowDebugOutput
  def fDelete(oSelf):
    assert oSelf.__fbDelete(bThrowErrors = True);
  @ShowDebugOutput
  def fbDelete(oSelf, bThrowErrors = False):
    return oSelf.__fbDelete(bThrowErrors);
  from .cFileSystemItem_fbDelete \
      import cFileSystemItem_fbDelete \
      as __fbDelete;
  
  def __repr__(oSelf):
    return "<%s %s #%d>" % (oSelf.__class__.__name__, oSelf, id(oSelf));
  def fsToString(oSelf):
    return "%s{%s#%d}" % (oSelf.__class__.__name__, oSelf.sPath, id(oSelf));
  def __str__(oSelf):
    return oSelf.sPath;