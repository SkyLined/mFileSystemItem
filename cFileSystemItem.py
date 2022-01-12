import os, re, zipfile;
from io import BytesIO;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = fShowDebugOutput = lambda x: x; # NOP

from mNotProvided import *;

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
  def __init__(oSelf, sPath = None, oParent = None):
    oSelf.sPath = fsGetNormalizedPath(sPath, oParent.sPath if oParent else None);
    if oParent:
      sParentPath = fsGetNormalizedPath(oSelf.sPath + os.sep + "..");
      assert sParentPath == oParent.sPath, \
          "Cannot create a child (path = %s, normalized = %s, parent = %s) for the given parent (path %s)" % \
          (repr(sPath), repr(oSelf.sPath), repr(sParentPath), repr(oParent.sPath));
    oSelf.sName = os.path.basename(oSelf.sPath);
    uDotIndex = oSelf.sName.rfind(".");
    oSelf.s0Extension = None if uDotIndex == -1 else oSelf.sName[uDotIndex + 1:];
    
    oSelf.__sWindowsPath = None;
    oSelf.__bWindowsPathSet = False;
    oSelf.__sDOSPath = None;
    oSelf.__bDOSPathSet = False;
    
    oSelf.__oRoot = oParent.oRoot if oParent else None;
    oSelf.__o0Parent = oParent;
    oSelf.__bParentSet = oParent is not None;
    oSelf.__o0PyFile = None;
    oSelf.__bPyFileIsInsideZipFile = False;
    oSelf.__o0PyZipFile = None;
    oSelf.__doPyZipInfo_by_sZipInternalPath = {};
    oSelf.__doPyFile_by_sZipInternalPath = {};
    oSelf.__dbWritable_by_sZipInternalPath = {};
    oSelf.__bWritable = False;
    return;
  
  @property
  def oParent(oSelf): # TODO: Should be depricated!!
    return oSelf.o0Parent;
  @property
  @ShowDebugOutput
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
  @ShowDebugOutput
  def oRoot(oSelf):
    if not oSelf.__oRoot:
      o0Parent = oSelf.o0Parent;
      oSelf.__oRoot = o0Parent.oRoot if o0Parent else oSelf;
    return oSelf.__oRoot;
  
  def fbIsInsideZipFile(oSelf, bThrowErrors = False):
    o0Parent = oSelf.o0Parent;
    if not o0Parent:
      # If it does not have a parent, it cannot be in a zip file.
      fShowDebugOutput("root cannot be in a zip file");
      return False;
    # create a list of ancestors, top most last.
    aoAncestors = [];
    while o0Parent:
      aoAncestors.append(o0Parent);
      o0Parent = o0Parent.o0Parent;
    # start from the top, see if the ancestor:
    # * is open as a zip file -> return True
    # * does no exists on the file system -> return False
    # * is a valid zip file -> return True
    # If non of the ancestors have any of the above trades -> return False
    while aoAncestors:
      oAncestor = aoAncestors.pop(0);
      try:
        # If it exists in the file system according to the OS, it is not in a .zip
        if oAncestor.fbIsOpenAsZipFile(bThrowErrors = False):
          return True;
        elif not os.path.exists(oAncestor.sWindowsPath):
          return False;
        elif oAncestor.fbIsValidZipFile(bThrowErrors = False):
          return True;
      except:
        if bThrowErrors:
          raise;
    # None of the ancestors was open as or a valid zip file.
    return False;
  
  def fo0GetZipRoot(oSelf, bThrowErrors = False):
     # If it exists in the file system according to the OS, it is not in a .zip
    try:
      if os.path.exists(oSelf.sWindowsPath):
        fShowDebugOutput("file exists so cannot have a zip root");
        return None;
    except:
      if bThrowErrors:
        raise;
    o0Parent = oSelf.o0Parent;
    if not o0Parent:
      # If it does not have a parent, it cannot be in a zip file.
      fShowDebugOutput("root cannot have a zip root");
      return None;
    if o0Parent.fbIsValidZipFile(bParseZipFiles = True, bThrowErrors = bThrowErrors):
      # If its parent is a valid zip file, this is its zip root
      fShowDebugOutput("parent");
      return o0Parent;
    # This item inherits its zip root from its parent.
    fShowDebugOutput("ancestor");
    return o0Parent.fo0GetZipRoot(bThrowErrors = bThrowErrors);
  
  def __del__(oSelf):
    if oSelf.__o0PyZipFile:
      try:
        oSelf.__o0PyZipFile.close();
      except Exception:
        pass;
    if oSelf.__o0PyFile:
      if oSelf.__bPyFileIsInsideZipFile:
        o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
        assert o0ZipRoot, \
            "Cannot find zip root for file %s" % (oSelf.sPath,);
        assert o0ZipRoot.__ZipFile_fbClosePyFile(oSelf.sPath, oSelf.__o0PyFile, bThrowErrors), \
            "Cannot close zip file %s in zip file %s" % (oSelf.sPath, o0ZipRoot.sPath);
        oSelf.__bPyFileIsInsideZipFile = False;
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
    from mWindowsSDK.mKernel32 import oKernel32DLL;
    from mWindowsSDK import LPCWSTR, FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_READONLY, DWORD;
    uFlags = oKernel32DLL.GetFileAttributesW(LPCWSTR(oSelf.sWindowsPath)).fuGetValue();
    oSelf.__bWasHiddenBeforeOpen = (uFlags & FILE_ATTRIBUTE_HIDDEN) != 0;
    if oSelf.__bWasHiddenBeforeOpen:
      uFlags -= FILE_ATTRIBUTE_HIDDEN;
    oSelf.__bWasReadOnlyBeforeOpen = (uFlags & FILE_ATTRIBUTE_READONLY) != 0;
    if oSelf.__bWasReadOnlyBeforeOpen:
      uFlags -= FILE_ATTRIBUTE_READONLY;
    if oSelf.__bWasHiddenBeforeOpen or oSelf.__bWasReadOnlyBeforeOpen:
      oKernel32DLL.SetFileAttributesW(LPCWSTR(oSelf.sWindowsPath), DWORD(uFlags));
  
  def __fReapplyAccessLimitingAttributesAfterOperation(oSelf):
    if oSelf.__bWasHiddenBeforeOpen or oSelf.__bWasReadOnlyBeforeOpen:
      from mWindowsSDK.mKernel32 import oKernel32DLL;
      from mWindowsSDK import LPCWSTR, FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_READONLY, DWORD;
      uFlags = oKernel32DLL.GetFileAttributesW(LPCWSTR(oSelf.sWindowsPath)).fuGetValue();
      if oSelf.__bWasHiddenBeforeOpen:
        uFlags |= FILE_ATTRIBUTE_HIDDEN;
      if oSelf.__bWasReadOnlyBeforeOpen:
        uFlags |= FILE_ATTRIBUTE_READONLY;
      oKernel32DLL.SetFileAttributesW(LPCWSTR(oSelf.sWindowsPath), DWORD(uFlags));
  
  @ShowDebugOutput
  def fsGetRelativePathTo(oSelf, sAbsoluteDescendantPath_or_oDescendant, bThrowErrors = False):
    sAbsoluteDescendantPath = (
      sAbsoluteDescendantPath_or_oDescendant.sPath if isinstance(sAbsoluteDescendantPath_or_oDescendant, cFileSystemItem) \
      else sAbsoluteDescendantPath_or_oDescendant
    );
    if (
      not sAbsoluteDescendantPath.startswith(oSelf.sPath)
      or sAbsoluteDescendantPath[len(oSelf.sPath):len(oSelf.sPath) + 1] not in [os.sep, os.altsep]
    ):
      fShowDebugOutput("not a descendant");
      assert not bThrowErrors, \
          "Cannot get relative path for %s as it is not a descendant of %s" % (sAbsoluteDescendantPath, oSelf.sPath);
      return None;
    return sAbsoluteDescendantPath[len(oSelf.sPath) + 1:];
  
  @property
  @ShowDebugOutput
  def sWindowsPath(oSelf):
    if not oSelf.__bWindowsPathSet:
      oSelf.__sWindowsPath = fsGetWindowsPath(oSelf.sPath);
      oSelf.__bWindowsPathSet = True;
    return oSelf.__sWindowsPath;
  
  @property
  @ShowDebugOutput
  def s0DOSPath(oSelf):
    if not oSelf.__bDOSPathSet:
      if not oSelf.fbIsInsideZipFile(bThrowErrors = False):
        oSelf.__sDOSPath = fs0GetDOSPath(oSelf.sPath);
      oSelf.__bDOSPathSet = True;
    return oSelf.__sDOSPath;
  
  def fuGetSize(oSelf, bParseZipFiles = False):
    return oSelf.fu0GetSize(bParseZipFiles = bParseZipFiles, bThrowErrors = True);
  def fu0GetSize(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if bParseZipFiles:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
      if o0ZipRoot:
        fShowDebugOutput("zip file");
        return o0ZipRoot.__ZipFile_fu0GetSize(oSelf.sPath, bThrowErrors);
    try:
      return os.path.getsize(oSelf.sWindowsPath);
    except Exception as oException:
      if bThrowErrors:
        raise;
      return None;
  
  def fuGetCompressedSize(oSelf):
    return oSelf.fu0GetCompressedSize(bThrowErrors = True);
  def fu0GetCompressedSize(oSelf, bThrowErrors = False): # bParseZipFiles == True is implied
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
    if not o0ZipRoot:
      return None;
    return o0ZipRoot.__ZipFile_fuGetCompressedSize(oSelf.sPath, bThrowErrors);
  
  @ShowDebugOutput
  def fbExists(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as zip file");
      return True;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as file");
      return True;
    try:
      if os.path.exists(oSelf.sWindowsPath):
        fShowDebugOutput("file/folder exists");
        return True;
    except:
      if bThrowErrors:
        raise;
    if bParseZipFiles:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
      if o0ZipRoot and o0ZipRoot.__ZipFile_fbContains(oSelf.sPath, bThrowErrors):
        fShowDebugOutput("zipped file exists");
        return True;
    return False;
  
  @ShowDebugOutput
  def fbIsFolder(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as zip file");
      return False;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as file");
      return False;
    try:
      if os.path.isdir(oSelf.sWindowsPath):
        fShowDebugOutput("is a folder");
        return True;
    except:
      if bThrowErrors:
        raise;
    if bParseZipFiles:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
      if o0ZipRoot and o0ZipRoot.__ZipFile_fbContainsFolder(oSelf.sPath, bThrowErrors):
        fShowDebugOutput("found in file path in zip file");
        return True;
    fShowDebugOutput("not found");
    return False;
  
  @ShowDebugOutput
  def fbIsFile(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as zip file");
      return True;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as file");
      return True;
    try:
      if os.path.isfile(oSelf.sWindowsPath):
        fShowDebugOutput("is a file");
        return True;
    except:
      if bThrowErrors:
        raise;
    if bParseZipFiles:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
      if o0ZipRoot and o0ZipRoot.__ZipFile_fbContainsFile(oSelf.sPath, bThrowErrors):
        fShowDebugOutput("found in zip file");
        return True;
    fShowDebugOutput("not found");
    return False;
  
  @ShowDebugOutput
  def fbIsValidZipFile(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as zip file");
      return True;
    if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("open as file");
      return False;
    # If the file exists, try to parse the .zip file to make sure it is valid
    try:
      if os.path.isfile(oSelf.sWindowsPath):
        try:
          zipfile.ZipFile(oSelf.sWindowsPath, "r").close();
        except (IOError, zipfile.BadZipfile) as oError:
          fShowDebugOutput("found but not valid");
          return False;
        else:
          fShowDebugOutput("found and valid");
          return True;
    except:
      if bThrowErrors:
        raise;
    if bParseZipFiles:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
      if o0ZipRoot:
        oPyFile = o0ZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWritable = False, bThrowErrors = bThrowErrors);
        if oPyFile:
          try:
            zipfile.ZipFile(oPyFile, "r").close();
          except zipfile.BadZipfile:
            fShowDebugOutput("found in zip file but not valid");
            return False;
          else:
            fShowDebugOutput("found in zip file and valid");
            return True;
          finally:
            # This should always succeed, so we always throw errors if it does not.
            o0ZipRoot.__ZipFile_fbClosePyFile(oSelf.sPath, oPyFile, bThrowErrors = True);
    fShowDebugOutput("not found");
    return False;
  
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
  
  def fCreateAsFolder(oSelf, bCreateParents = False, bParseZipFiles = False):
    assert oSelf.fbCreateAsFolder(
      bCreateParents = bCreateParents,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fbCreateAsFolder(oSelf, bCreateParents = False, bParseZipFiles = False, bThrowErrors = False):
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it is already open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it already exists as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it already exists!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    if bParseZipFiles and oSelf.fbIsInsideZipFile(bThrowErrors = bThrowErrors):
      # Zip files cannot have folders, so we will do nothing here. If a file is
      # created in this folder or one of its sub-folders, this folder will 
      # magically start to exist; in effect folders are virtual.
      fShowDebugOutput("folder in zip files are virtual");
      return True;
    else:
      if (
        oSelf.oParent
        and not oSelf.oParent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
      ):
        if not bCreateParents:
          assert not bThrowErrors, \
              "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
          return False;
        if not oSelf.oParent.fbCreateAsParent(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
          fShowDebugOutput("cannot create parent");
          return False;
      try:
        os.makedirs(oSelf.sWindowsPath);
        if not os.path.isdir(oSelf.sWindowsPath):
          fShowDebugOutput("makedirs succeeded but folder does not exist");
          return False;
      except Exception as oException:
        if bThrowErrors:
          raise;
        fShowDebugOutput("Exception: %s" % repr(oException));
        return False;
    fShowDebugOutput("folder created");
    return True;
  
  def faoGetChildren(oSelf, bParseZipFiles = False):
    return oSelf.fa0oGetChildren(
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fa0oGetChildren(oSelf, bParseZipFiles = False, bThrowErrors = False):
    if bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
      asChildNames = oSelf.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
    else:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
      if o0ZipRoot:
        asChildNames = o0ZipRoot.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
      elif oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        try:
          asChildNames = os.listdir(oSelf.sWindowsPath)
        except:
          if bThrowErrors:
            raise;
          fShowDebugOutput("cannot list folder");
          return None;
      elif bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
        asChildNames = oSelf.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
      else:
        fShowDebugOutput("not a folder%s" % (" or zip file" if bParseZipFiles else ""));
        return None;
    return [
      oSelf.__class__(oSelf.sPath + os.sep + sChildName, oSelf)
      for sChildName in sorted(asChildNames)
    ];
  
  def foGetChild(oSelf, sChildName, bParseZipFiles = False, bFixCase = False):
    return oSelf.fo0GetChild(
      sChildName,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
      bFixCase = bFixCase,
    );
  @ShowDebugOutput
  def fo0GetChild(oSelf, sChildName, bParseZipFiles = False, bThrowErrors = False, bFixCase = False):
    try:
      assert os.sep not in sChildName and os.altsep not in sChildName, \
          "Cannot create a child %s!" % sChildName;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    if bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
     asChildNames = oSelf.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
    else:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
      if o0ZipRoot:
        asChildNames = o0ZipRoot.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors) \
            if bParseZipFiles else [];
      elif (
        oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
        and bFixCase
      ):
        try:
          asChildNames = os.listdir(oSelf.sWindowsPath);
        except:
          if bThrowErrors:
            raise;
          asChildNames = [];
      else:
        asChildNames = [];
    # Look for an existing child that has the same name but different casing
    sLowerChildName = sChildName.lower();
    for sRealChildName in asChildNames:
      if sRealChildName.lower() == sLowerChildName:
        # Found one: use that name instead.
        sChildName = sRealChildName;
        break;
    oChild = oSelf.__class__(oSelf.sPath + os.sep + sChildName, oSelf);
    assert oSelf.fsGetRelativePathTo(oChild, bThrowErrors = bThrowErrors) == sChildName, \
        "Creating a child %s of %s resulted in a child path %s!" % (sChildName, oSelf.sPath, oChild.sPath);
    return oChild;
  
  def faoGetDescendants(oSelf, bParseZipFiles = False, bParseDescendantZipFiles = False):
    return oSelf.fa0oGetDescendants(
      bThrowErrors = True,
      bParseZipFiles = bParseZipFiles,
      bParseDescendantZipFiles = bParseDescendantZipFiles,
    );
  @ShowDebugOutput
  def fa0oGetDescendants(
    oSelf,
    bThrowErrors = False,
    bParseZipFiles = False,
    bParseDescendantZipFiles = False,
  ):
    aoDescendants = [];
    a0oChildren = oSelf.fa0oGetChildren(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
    if a0oChildren is None:
      fShowDebugOutput("cannot get list of children");
      return None;
    for oChild in a0oChildren:
      aoDescendants.append(oChild);
      if (
        oChild.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
        or (
          bParseDescendantZipFiles
          and oChild.fbIsValidZipFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
        )
      ):
        # oSelf or its parents can only be zip files if bParseZipFiles was true. If oSelf nor any of its
        # parents were zip files, setting bParseZipFiles has no affect. So we can use bParseZipFiles = true
        aoDescendants += oChild.fa0oGetDescendants(
          bThrowErrors = bThrowErrors,
          bParseZipFiles = bParseZipFiles,
          bParseDescendantZipFiles = bParseDescendantZipFiles,
        ) or [];
    return aoDescendants;
  
  def foGetDescendant(oSelf, sDescendantRelativePath, bFixCase = False, bParseZipFiles = False):
    return oSelf.fo0GetDescendant(
      sDescendantRelativePath,
      bFixCase = bFixCase,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fo0GetDescendant(
    oSelf,
    sDescendantRelativePath,
    bFixCase = False,
    bParseZipFiles = False,
    bThrowErrors = False,
  ):
    sChildName = sDescendantRelativePath.split(os.sep, 1)[0].split(os.altsep, 1)[0];
    assert sChildName, \
        "Cannot get descendant %s of %s because the path is absolute!" % (sDescendantRelativePath, oSelf.sPath);
    sChildDescendantPath = sDescendantRelativePath[len(sChildName) + 1:];
    o0Child = oSelf.fo0GetChild(
      sChildName,
      bFixCase = bFixCase,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = bThrowErrors,
    );
    if o0Child is None:
      return None;
    o0Descendant = (
      o0Child if not sChildDescendantPath else \
      o0Child.fo0GetDescendant(
        sChildDescendantPath,
        bFixCase = bFixCase,
        bParseZipFiles = bParseZipFiles,
        bThrowErrors = bThrowErrors,
      )
    );
    return o0Descendant;
  
  def fSetAsCurrentWorkingDirectory(oSelf):
    assert oSelf.fbSetAsCurrentWorkingDirectory(bThrowErrors = True);
  @ShowDebugOutput
  def fbSetAsCurrentWorkingDirectory(oSelf, bThrowErrors = False):
    try:
      # CWD cannot be a zip file so not bParseZipFiles argument exists.
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot set zip file %s as current working directory!" % oSelf.sPath;
      assert (
        not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors)
        and not oSelf.fbIsFile(bParseZipFiles = False, bThrowErrors = bThrowErrors)
      ), \
          "Cannot set file %s as current working directory!" % oSelf.sPath;
      assert oSelf.fbExists(bParseZipFiles = False, bThrowErrors = bThrowErrors), \
          "Cannot set folder %s as current working directory if it does not exist!" % oSelf.sPath;
      assert oSelf.fbIsFolder(bParseZipFiles = False, bThrowErrors = bThrowErrors), \
          "Cannot set folder %s as current working directory if it is not a folder!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    # If the cwd is already the path of this cFileSystemItem, do nothing.
    if os.getcwd() != oSelf.sPath:
      # Try using the basic path
      try:
        os.chdir(oSelf.sPath);
      except:
        pass; # We may need to use the windows path, so don't throw an error yet.
      if os.getcwd() != oSelf.sPath:
        # Try using the windows path.
        try:
          os.chdir(oSelf.sWindowsPath);
        except:
          if bThrowErrors:
            raise;
          pass;
    bSuccess = fsGetWindowsPath(os.getcwd()) == oSelf.sWindowsPath;
    return bSuccess;
  
  def fCreateAsFile(oSelf, sbData = b"", bCreateParents = False, bParseZipFiles = False, bKeepOpen = False):
    assert oSelf.fbCreateAsFile(
      sbData = sbData,
      bCreateParents = bCreateParents,
      bParseZipFiles = bParseZipFiles,
      bKeepOpen = bKeepOpen,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fbCreateAsFile(
    oSelf,
    sbData = b"",
    bCreateParents = False,
    bParseZipFiles = False,
    bKeepOpen = False,
    bThrowErrors = False,
  ):
    try:
      assert oSelf.oParent, \
          "Cannot create file %s as a root node!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create file %s when it is already open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create file %s if it already exists as a folder!" % oSelf.sPath;
      assert not oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create file %s if it already exists!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if o0ZipRoot:
      oSelf.__o0PyFile = o0ZipRoot.__ZipFile_foCreateFile(oSelf.sPath, sbData, bKeepOpen, bThrowErrors);
      if not oSelf.__o0PyFile:
        fShowDebugOutput("Cannot create file in zip file");
        return False;
      oSelf.__bPyFileIsInsideZipFile = True;
      oSelf.__bWasReadOnlyBeforeOpen = False;
      oSelf.__bWasHiddenBeforeOpen = False;
      if not bKeepOpen: # __ZipFile_foCreateFile will return True if bKeepOpen is False.
        oSelf.__o0PyFile = None;
        oSelf.__bPyFileIsInsideZipFile = False;
      else:
        oSelf.__bWritable = True;
    else:
      if not oSelf.oParent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        if not bCreateParents:
          assert not bThrowErrors, \
              "Cannot create file %s when its parent does not exist!" % oSelf.sPath;
          return False;
        if not oSelf.oParent.fbCreateAsParent(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
          fShowDebugOutput("Cannot create parent");
          return False;
      try:
        oSelf.__o0PyFile = open(oSelf.sWindowsPath, "wb");
        oSelf.__bPyFileIsInsideZipFile = False;
        oSelf.__bWasReadOnlyBeforeOpen = False;
        oSelf.__bWasHiddenBeforeOpen = False;
        oSelf.__bWritable = True;
        try:
          oSelf.__o0PyFile.write(sbData);
        finally:
          if not bKeepOpen:
            oSelf.__o0PyFile.close();
            oSelf.__o0PyFile = None;
            oSelf.__bPyFileIsInsideZipFile = False;
            oSelf.__bWritable = False;
      except Exception as oException:
        if bThrowErrors:
          raise;
        fShowDebugOutput("Exception: %s" % repr(oException));
        return False;
    return True;
  
  @ShowDebugOutput
  def fbOpenAsFile(oSelf, bWritable = False, bAppend = False, bParseZipFiles = False, bThrowErrors = False):
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot open file %s twice!" % oSelf.sPath;
      assert oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it does not exist!" % oSelf.sPath;
      assert oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it is not a file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if o0ZipRoot:
      oSelf.__o0PyFile = o0ZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWritable, bThrowErrors);
      if not oSelf.__o0PyFile:
        fShowDebugOutput("Cannot open file in zip file");
        return False;
      oSelf.__bPyFileIsInsideZipFile = True;
      oSelf.__bWasReadOnlyBeforeOpen = False;
      oSelf.__bWasHiddenBeforeOpen = False;
    else:
      oSelf.__fRemoveAccessLimitingAttributesBeforeOperation();
      try:
        oSelf.__o0PyFile = open(oSelf.sWindowsPath, ("a+b" if bAppend else "wb") if bWritable else "rb");
      except Exception as oException:
        oSelf.__fReapplyAccessLimitingAttributesAfterOperation();
        if bThrowErrors:
          raise;
        fShowDebugOutput("Exception: %s" % repr(oException));
        return False;
      oSelf.__bPyFileIsInsideZipFile = False;
    oSelf.__bWritable = bWritable;
    return True;
  
  def fsbRead(oSelf, bKeepOpen = None, bParseZipFiles = True):
    return oSelf.fsb0Read(
      bKeepOpen = bKeepOpen,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fsb0Read(oSelf, bKeepOpen = None, bParseZipFiles = True, bThrowErrors = False):
    # Note that we assume that the caller wants us to parse zip files, unlike most other functions!
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot read file %s when it is open as a zip file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    # Keep the file open if it is already open, or the special argument is provided.
    # Close or keep the file open depending on the argument, or whether it is currently open if it is not provided.
    bIsOpen = oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors);
    bKeepOpen = bKeepOpen if bKeepOpen is not None else bIsOpen; 
    # Make sure the file is open
    if not bIsOpen:
      if not oSelf.fbOpenAsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        fShowDebugOutput("cannot open file");
        return None;
    try:
      sbData = oSelf.__o0PyFile.read();
    except Exception as oException:
      if bThrowErrors:
        raise;
      fShowDebugOutput("Exception: %s" % oException);
      return None;
    finally:
      if not bKeepOpen:
        # This must always succeed, so it will always throw errors if it does not.
        oSelf.fClose();
    return sbData;
  
  def fWrite(oSelf, sbData, bAppend = False, bKeepOpen = None, bParseZipFiles = True):
    return oSelf.fbWrite(
      sbData,
      bAppend = bAppend,
      bKeepOpen = bKeepOpen,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fbWrite(oSelf, sbData, bAppend = False, bKeepOpen = None, bParseZipFiles = True, bThrowErrors = False):
    try:
      # Note that we assume that the caller wants us to parse zip files, unlike most other functions!
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot write file %s when it is open as a zip file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    # Close or keep the file open depending on the argument, or whether it is currently open if it is not provided.
    bIsOpen = oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors);
    bKeepOpen = bKeepOpen if bKeepOpen is not None else bIsOpen; 
    # Make sure the file is open and writable
    if not bIsOpen:
      if not oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        if not oSelf.fbCreateAsFile(
          sbData,
          bKeepOpen = bKeepOpen,
          bParseZipFiles = bParseZipFiles,
          bThrowErrors = bThrowErrors,
        ):
          fShowDebugOutput("cannot create file");
          return False;
        return True;
      if not oSelf.fbOpenAsFile(
        bWritable = True,
        bAppend = bAppend,
        bParseZipFiles = bParseZipFiles,
        bThrowErrors = bThrowErrors,
      ):
        fShowDebugOutput("cannot open file");
        return False;
    try:
      oSelf.__o0PyFile.write(sbData);
    except Exception as oException:
      if bThrowErrors:
        raise;
      fShowDebugOutput("Exception: %s" % oException);
      return False;
    finally:
      if not bKeepOpen:
        # This should alwyas succeed so it will always throw errors if it does not.
        oSelf.fClose();
    return True;
  
  def fCreateAsZipFile(oSelf, bKeepOpen = False, bCreateParents = False, bParseZipFiles = False):
    assert oSelf.fbCreateAsZipFile(
      bKeepOpen = bKeepOpen,
      bCreateParents = bCreateParents,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fbCreateAsZipFile(
    oSelf,
    bKeepOpen = False,
    bCreateParents = False,
    bParseZipFiles = False,
    bThrowErrors = False,
  ):
    try:
      assert oSelf.oParent, \
          "Cannot create zip file %s as a root node!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create zip file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create zip file %s when it is already open as a file!" % oSelf.sPath;
      assert not oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create zip file %s if it already exists!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if o0ZipRoot:
      oSelf.__o0PyFile = o0ZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWritable = True, bThrowErrors = bThrowErrors);
      if not oSelf.__o0PyFile:
        fShowDebugOutput("Cannot create file as zip file");
        return False;
      oSelf.__bPyFileIsInsideZipFile = True;
    else:
      if not oSelf.oParent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        if not bCreateParents:
          assert not bThrowErrors, \
              "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
          return False;
        if not oSelf.oParent.fbCreateAsParent(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
          return False;
      # Open/create the file as writable and truncate it if it already existed.
      try:
        oSelf.__o0PyFile = open(oSelf.sWindowsPath, "wb");
      except:
        if bThrowErrors:
          raise;
        return False;
      oSelf.__bPyFileIsInsideZipFile = False;
    oSelf.__bWasReadOnlyBeforeOpen = False;
    oSelf.__bWasHiddenBeforeOpen = False;
    oSelf.__bWritable = True;
    try:
      oSelf.__o0PyFile.write(b"");
      oSelf.__o0PyZipFile = zipfile.ZipFile(oSelf.__o0PyFile, "w");
      oSelf.__doPyZipInfo_by_sZipInternalPath = {};
    except:
      # This should always succeed so it will always throw errors if it does not
      oSelf.fClose();
      if bThrowErrors:
        raise;
      return False;
    if not bKeepOpen:
      # This should always succeed so it will always throw errors if it does not
      oSelf.fClose();
    return True;
  
  @ShowDebugOutput
  def fbOpenAsZipFile(oSelf, bWritable = False, bParseZipFiles = False, bThrowErrors = False):
    try:
      # Note that bParseZipFiles applies to its parents.
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot open zip file %s twice!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot open zip file %s when it is already open as a file!" % oSelf.sPath;
      assert oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot open zip file %s if it does not exist!" % oSelf.sPath;
      assert oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot open zip file %s when it is not a file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if o0ZipRoot:
      oSelf.__o0PyFile = o0ZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWritable, bThrowErrors);
      if not oSelf.__o0PyFile:
        return False;
      oSelf.__bPyFileIsInsideZipFile = True;
      oSelf.__bWasReadOnlyBeforeOpen = False;
      oSelf.__bWasHiddenBeforeOpen = False;
    else:
      oSelf.__fRemoveAccessLimitingAttributesBeforeOperation();
      try:
        oSelf.__o0PyFile = open(oSelf.sWindowsPath, "a+b" if bWritable else "rb");
      except:
        oSelf.__fReapplyAccessLimitingAttributesAfterOperation();
        if bThrowErrors:
          raise;
        return False;
      oSelf.__bPyFileIsInsideZipFile = False;
    try:
      oSelf.__o0PyZipFile = zipfile.ZipFile(
        oSelf.__o0PyFile,
        "a" if bWritable else "r",
        zipfile.ZIP_DEFLATED,
      );
      oSelf.__doPyZipInfo_by_sZipInternalPath = None;
    except:
      # This should always succeed so it will always throw errors if it does not
      oSelf.fClose();
      if bThrowErrors:
        raise;
      return False;
    oSelf.__bWritable = bWritable;
    return True;
  
  def fCreateAsParent(oSelf, bParseZipFiles = False):
    assert oSelf.fbCreateAsParent(
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fbCreateAsParent(oSelf, bParseZipFiles = False, bThrowErrors = False):
    bIsZipFile = oSelf.s0Extension and oSelf.s0Extension.lower() == "zip";
    sCreateAsType = "zip file" if bIsZipFile else "folder";
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create %s %s when it is already open as a zip file!" % (sCreateAsType, oSelf.sPath);
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create %s %s when it is already open as a file!" % (sCreateAsType, oSelf.sPath);
      assert not oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create %s %s when it already exists as a file!" % (sCreateAsType, oSelf.sPath);
      if not bIsZipFile and bParseZipFiles:
        o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
        if o0ZipRoot:
          # Folders cannot be stored within a zip file; only files can be stored with a relative
          # path that contain folder names. So, if we are asked to create a parent folder it must
          # be for such a file that has this parent folder in its path. This means no action is
          # needed: the folder will magically exists once the file is created. Except that we do
          # need to create the zip file that contains this folder if it does not exists. If the
          # file exists, we should check it already exists:
          if not o0ZipRoot.fbExists(bParseZipFiles = True, bThrowErrors = bThrowErrors):
            return o0ZipRoot.fbCreateAsZipFile(
              bCreateParents = True,
              bParseZipFiles = bParseZipFiles,
              bThrowErrors = bThrowErrors,
            );
          assert o0ZipRoot.fbIsValidZipFile(bParseZipFiles = True, bThrowErrors = bThrowErrors), \
              "Cannot create folder %s when %s is not a valid zip file!" % (oSelf.sPath, o0ZipRoot.sPath);
          return True;
      assert not oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create %s %s when it already exists as a folder!" % (sCreateAsType, oSelf.sPath);
      assert not oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create %s %s if it already exists!" % (sCreateAsType, oSelf.sPath);
      assert oSelf.oParent, \
          "Cannot create %s %s as it is a root node!" % (sCreateAsType, oSelf.sPath);
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    if (
      not oSelf.oParent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
      and not oSelf.oParent.fbCreateAsParent(
        bParseZipFiles = bParseZipFiles,
        bThrowErrors = bThrowErrors,
      )
    ):
      return False;
    if bIsZipFile and bParseZipFiles:
      return oSelf.fbCreateAsZipFile(
        bCreateParents = True,
        bParseZipFiles = True,
        bThrowErrors = bThrowErrors,
      );
    return Self.fbCreateAsFolder(
      bCreateParents = True,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = bThrowErrors,
    );
  
  def fbIsOpenAsFile(oSelf, bThrowErrors = False):
    return oSelf.__o0PyFile is not None and not oSelf.__o0PyZipFile is not None;
  def fbIsOpenAsZipFile(oSelf, bThrowErrors = False):
    return oSelf.__o0PyZipFile is not None;
  def fbIsOpen(oSelf, bThrowErrors = False):
    return oSelf.__o0PyFile is not None;
  
  def fClose(oSelf):
    oSelf.fbClose(bThrowErrors = True);
  @ShowDebugOutput
  def fbClose(oSelf, bThrowErrors = False):
    try:
      assert (
        oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors)
        or oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors)
      ), \
          "Cannot close %s when it is not open!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    if oSelf.__o0PyZipFile:
      try:
        oSelf.__o0PyZipFile.close();
      except:
        if bThrowErrors:
          raise;
        return False;
      oSelf.__o0PyZipFile = None;
      oSelf.__doPyZipInfo_by_sZipInternalPath = None;
    if oSelf.__o0PyFile:
      if oSelf.__bPyFileIsInsideZipFile:
        o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
        assert o0ZipRoot, \
            "Cannot find zip root for file %s" % (oSelf.sPath,);
        assert o0ZipRoot.__ZipFile_fbClosePyFile(oSelf.sPath, oSelf.__o0PyFile, bThrowErrors), \
            "Cannot close zip file %s in zip file %s" % (oSelf.sPath, o0ZipRoot.sPath);
      else:
        try:
          oSelf.__o0PyFile.close();
        except:
          if bThrowErrors:
            raise;
          return False;
      oSelf.__fReapplyAccessLimitingAttributesAfterOperation();
      oSelf.__o0PyFile = None;
      oSelf.__bPyFileIsInsideZipFile = False;
    oSelf.__bWritable = False;
    return True;
  
  @ShowDebugOutput
  def fbRename(oSelf, sNewName, bParseZipFiles = True, bThrowErrors = False):
    try:
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot rename %s when it is open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot rename %s when it is open as a zip file!" % oSelf.sPath;
      if bParseZipFiles:
        assert not oSelf.fbIsInsideZipFile(bThrowErrors = bThrowErrors), \
            "Renaming is not implemented within zip files!";
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    o0NewItem = oSelf.oParent.fo0GetChild(
      sNewName,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = bThrowErrors,
    );
    if o0NewItem is None:
      return False;
    try:
      os.rename(oSelf.sWindowsPath, o0NewItem.sWindowsPath);
    except:
      if bThrowErrors:
        raise;
      return False;
    if not o0NewItem.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      return False;
    oSelf.sPath = o0NewItem.sPath;
    oSelf.sName = o0NewItem.sName;
    oSelf.s0Extension = o0NewItem.s0Extension;
    oSelf.__sWindowsPath = o0NewItem.__sWindowsPath;
    oSelf.__bWindowsPathSet = o0NewItem.__bWindowsPathSet;
    oSelf.__sDOSPath = o0NewItem.__sDOSPath;
    oSelf.__bDOSPathSet = o0NewItem.__bDOSPathSet;
    return True;
  
  @ShowDebugOutput
  def fbMove(oSelf, oNewItem, bParseZipFiles = True, bThrowErrors = False):
    try:
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot rename %s when it is open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot rename %s when it is open as a zip file!" % oSelf.sPath;
      if bParseZipFiles:
        assert not oSelf.fbIsInsideZipFile(bThrowErrors = bThrowErrors), \
            "moving is not implemented within zip files!";
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    try:
      os.rename(oSelf.sWindowsPath, oNewItem.sWindowsPath);
    except:
      if bThrowErrors:
        raise;
      return False;
    if not oNewItem.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      return False;
    oSelf.sPath = oNewItem.sPath;
    oSelf.sName = oNewItem.sName;
    oSelf.s0Extension = oNewItem.s0Extension;
    oSelf.__sWindowsPath = oNewItem.__sWindowsPath;
    oSelf.__bWindowsPathSet = oNewItem.__bWindowsPathSet;
    oSelf.__sDOSPath = oNewItem.__sDOSPath;
    oSelf.__bDOSPathSet = oNewItem.__bDOSPathSet;
    return True;
  
  def fDeleteDescendants(oSelf, bClose = False, bParseZipFiles = True):
    return oSelf.fbDeleteDescendants(
      bClose = bClose,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fbDeleteDescendants(oSelf, bClose = False, bParseZipFiles = True, bThrowErrors = False):
    try:
      if bClose:
        if not oSelf.fbClose(bThrowErrors = bThrowErrors):
          return False;
      else:
        assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
            "Cannot delete %s when it is open as a zip file!" % oSelf.sPath;
        assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
            "Cannot delete %s when it is open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot delete descendants of %s when it is a file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    a0oChildren = oSelf.fa0oGetChildren(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
    if a0oChildren is None:
      return False;
    for oChild in a0oChildren:
      if not oChild.fbDelete(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        return False;
    return True;
  
  def fDelete(oSelf, bClose = False, bParseZipFiles = True):
    return oSelf.fbDelete(
      bClose = bClose,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = True,
    );
  @ShowDebugOutput
  def fbDelete(oSelf, bClose = False, bParseZipFiles = True, bThrowErrors = False):
    try:
      if bClose:
        if not oSelf.fbClose(bThrowErrors = bThrowErrors):
          return False;
      else:
        assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
            "Cannot delete %s when it is open as a zip file!" % oSelf.sPath;
        assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
            "Cannot delete %s when it is open as a file!" % oSelf.sPath;
      if bParseZipFiles:
        assert not oSelf.fbIsInsideZipFile(bThrowErrors = bThrowErrors), \
            "Deleting is not implemented within zip files!";
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
    # Handle descendants if any
    bIsFolder = oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
    if bIsFolder and not oSelf.fbDeleteDescendants(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      return False;
    # Remive hidden/read-only attributes;
    oSelf.__fRemoveAccessLimitingAttributesBeforeOperation();
    # Delete folder or file
    try:
      os.rmdir(oSelf.sWindowsPath) if bIsFolder else os.remove(oSelf.sWindowsPath);
    except:
      if bThrowErrors:
        raise;
      return False;
    # Make sure it no longer exists
    if oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      if bThrowErrors:
        raise AssertionError("Folder %s exists after being removed!?" % oSelf.sPath);
      return False;
    return True;
  
  @property
  def __ZipFile_doPyZipInfo_by_sZipInternalPath(oSelf):
    if oSelf.__doPyZipInfo_by_sZipInternalPath is None:
      oSelf.__doPyZipInfo_by_sZipInternalPath = dict([
        (oPyZipInfo.filename, oPyZipInfo)
        for oPyZipInfo in oSelf.__o0PyZipFile.infolist()
      ]);
    return oSelf.__doPyZipInfo_by_sZipInternalPath;
    
  def __ZipFile_fbContains(oSelf, sPath, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot check if %s contains %s if it cannot be opened!" % (oSelf.sPath, sPath);
    try:
      sWantedZipInternalPath = oSelf.fsGetRelativePathTo(
        sPath,
        bThrowErrors = bThrowErrors,
      ).replace(os.altsep, "/").replace(os.sep, "/");
      for sZipInternalPath in oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath.keys():
        if (
          sZipInternalPath.startswith(sWantedZipInternalPath)
          and sZipInternalPath[len(sWantedZipInternalPath):len(sWantedZipInternalPath) + 1] in ["", os.sep]
        ):
          return True;
      return False;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close %s" % oSelf.sPath;
  
  def __ZipFile_fbContainsFolder(oSelf, sPath, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot check if %s contains a folder %s if it cannot be opened!" % (oSelf.sPath, sPath);
    try:
      sWantedZipInternalPathHeader = oSelf.fsGetRelativePathTo(
        sPath,
        bThrowErrors = bThrowErrors,
      ).replace(os.altsep, "/").replace(os.sep, "/") + "/";
      for sZipInternalPath in oSelf.__doPyZipInfo_by_sZipInternalPath.keys():
        if sZipInternalPath.startswith(sWantedZipInternalPathHeader):
          return True;
      return False;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close %s" % oSelf.sPath;
  
  def __ZipFile_fbContainsFile(oSelf, sPath, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot check if %s contains a file %s if it cannot be opened!" % (oSelf.sPath, sPath);
    try:
      sZipInternalPath = oSelf.fsGetRelativePathTo(
        sPath,
        bThrowErrors = bThrowErrors,
      ).replace(os.altsep, "/").replace(os.sep, "/");
      return sZipInternalPath in oSelf.__doPyZipInfo_by_sZipInternalPath.keys();
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close %s" % oSelf.sPath;
  
  def __ZipFile_foCreateFile(oSelf, sPath, sbData, bKeepOpen, bThrowErrors):
    fAssertType("sbData", sbData, bytes);
    bZipFileMustBeClosed = False;
    if not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors):
      bZipFileMustBeClosed = True;
      assert oSelf.fbOpenAsZipFile(bWritable = True, bThrowErrors = bThrowErrors), \
          "Cannot create a file %s in %s if it cannot be opened!" % (sPath, oSelf.sPath);
    sZipInternalPath = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace(os.altsep, "/").replace(os.sep, "/");
    assert sZipInternalPath not in oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath, \
        "Cannot create/overwrite existing file %s in zip file %s!" % (sPath, oSelf.sPath);
    try:
      try:
        oSelf.__o0PyZipFile.writestr(sZipInternalPath, sbData, zipfile.ZIP_DEFLATED);
      except:
        if bThrowErrors:
          raise;
        return None;
      # Update the cached list of ZipInfo objects by file name
      oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath[sZipInternalPath] = \
          oSelf.__o0PyZipFile.getinfo(sZipInternalPath);
      if bKeepOpen:
        oPyFile = BytesIO();
        oPyFile.write(sbData);
        oPyFile.seek(0);
        oSelf.__doPyFile_by_sZipInternalPath[sZipInternalPath] = oPyFile;
        oSelf.__dbWritable_by_sZipInternalPath[sZipInternalPath] = bWritable;
        return oPyFile;
      return True;
    finally:
      if bZipFileMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close %s" % oSelf.sPath;
  
  def __ZipFile_foOpenPyFile(oSelf, sPath, bWritable, bThrowErrors):
    sZipInternalPath = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace(os.altsep, "/").replace(os.sep, "/");
    assert sZipInternalPath not in oSelf.__doPyFile_by_sZipInternalPath, \
        "Cannot open file %s in zip file %s if it is already open!" % (sPath, oSelf.sPath);
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
    try:
      if sZipInternalPath in oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath:
        sbData = oSelf.__o0PyZipFile.read(sZipInternalPath);
        oPyFile = BytesIO();
        oPyFile.write(sbData);
        oPyFile.seek(0);
      else:
        assert bWritable, \
            "Cannot open file %s in zip file %s for reading if it does not exist!" % (sPath, oSelf.sPath);
        oPyFile = BytesIO();
      oSelf.__doPyFile_by_sZipInternalPath[sZipInternalPath] = oPyFile;
      oSelf.__dbWritable_by_sZipInternalPath[sZipInternalPath] = bWritable;
      return oPyFile;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close zip file %s!" % oSelf.sPath;
    raise AssertionError("Cannot file %s in zip file %s!" % (sPath, oSelf.sPath));
  
  def __ZipFile_fbClosePyFile(oSelf, sPath, oPyFile, bThrowErrors):
    sZipInternalPath = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace(os.altsep, "/").replace(os.sep, "/");
    bWritable = oSelf.__dbWritable_by_sZipInternalPath[sZipInternalPath];
    if bWritable:
      bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
      if bMustBeClosed:
        assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
            "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
      assert sZipInternalPath not in oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath, \
          "Cannot create/overwrite existing file %s in zip file %s!" % (sPath, oSelf.sPath);
      assert sZipInternalPath in oSelf.__doPyFile_by_sZipInternalPath \
          and sZipInternalPath in oSelf.__dbWritable_by_sZipInternalPath, \
          "Cannot close file %s in zip file %s if it is not open!" % (sPath, oSelf.sPath);
      assert oPyFile == oSelf.__doPyFile_by_sZipInternalPath[sZipInternalPath], \
          "Internal inconsistency!";
      try:
        # We assume writable files have been modifed and need to be saved in the zip file.
        try:
          oPyFile.seek(0);
          sbData = oPyFile.read();
          oSelf.__o0PyZipFile.writestr(sZipInternalPath, sbData);
        except:
          if bThrowErrors:
            raise;
          return False;
        oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath[sZipInternalPath] = \
            oSelf.__o0PyZipFile.getinfo(sZipInternalPath);
      finally:
        if bMustBeClosed:
          assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
              "Cannot close zip file %s!" % oSelf.sPath;
    del oSelf.__doPyFile_by_sZipInternalPath[sZipInternalPath];
    del oSelf.__dbWritable_by_sZipInternalPath[sZipInternalPath];
    return True;
  
  def __ZipFile_fasGetChildNames(oSelf, sPath, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
    try:
      sWantedZipInternalPathHeader = (
        "" if sPath == oSelf.sPath
        else oSelf.fsGetRelativePathTo(
          sPath,
          bThrowErrors = bThrowErrors,
        ).replace(os.altsep, "/").replace(os.sep, "/") + "/"
      );
      uMinLength = len(sWantedZipInternalPathHeader); # Used to speed things up
      asChildNames = [];
      for sZipInternalPath in oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath.keys():
        if len(sZipInternalPath) > uMinLength and sZipInternalPath.startswith(sWantedZipInternalPathHeader):
          sZipInternalRelativePath = sZipInternalPath[len(sWantedZipInternalPathHeader):];
          sChildName = sZipInternalRelativePath.split("/", 1)[0];
          if sChildName not in asChildNames:
            asChildNames.append(sChildName);
      return asChildNames;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close zip file %s!" % oSelf.sPath;
   
  def __ZipFile_fu0GetSize(oSelf, sPath, bThrowErrors):
    sZipInternalPath = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace(os.altsep, "/").replace(os.sep, "/");
    if oSelf.__dbWritable_by_sZipInternalPath.get(sZipInternalPath):
      # If it is open for writing, we're always writing at the end of the file.
      # Since `tell()` returns the offet from the start of the file where writing will happen, it returns the number
      # of bytes in the file:
      oPyFile = oSelf.__doPyFile_by_sZipInternalPath[sZipInternalPath];
      return oPyFile.tell();
    oPyZipInfo = oSelf.__ZipFile_foGetZipInfo(sPath, bThrowErrors);
    return oPyZipInfo.file_size;
  
  def __ZipFile_fuGetCompressedSize(oSelf, sPath, bThrowErrors):
    sZipInternalPath = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace(os.altsep, "/").replace(os.sep, "/");
    assert not oSelf.__dbWritable_by_sZipInternalPath.get(sZipInternalPath), \
        "Cannot get compressed sized of a file that is open for writing; please close it first!";
    oPyZipInfo = oSelf.__ZipFile_foGetZipInfo(sPath, bThrowErrors);
    return oPyZipInfo.compress_size;
  
  def __ZipFile_foGetZipInfo(oSelf, sPath, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bWritable = False, bThrowErrors = bThrowErrors), \
          "Cannot check if %s contains a file %s if it cannot be opened!" % (oSelf.sPath, sPath);
    try:
      sZipInternalPath = oSelf.fsGetRelativePathTo(
        sPath,
        bThrowErrors = bThrowErrors,
      ).replace(os.altsep, "/").replace(os.sep, "/");
      assert sZipInternalPath in oSelf.__ZipFile_doPyZipInfo_by_sZipInternalPath, \
          "Cannot get file size for non-existing file %s in zip file %s!" % (sPath, oSelf.sPath);
      return oSelf.__doPyZipInfo_by_sZipInternalPath[sZipInternalPath];
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close %s" % oSelf.sPath;
      
  def __repr__(oSelf):
    return "<%s %s #%d>" % (oSelf.__class__.__name__, oSelf, id(oSelf));
  def fsToString(oSelf):
    return "%s{%s#%d}" % (oSelf.__class__.__name__, oSelf.sPath, id(oSelf));
  def __str__(oSelf):
    return oSelf.sPath;

