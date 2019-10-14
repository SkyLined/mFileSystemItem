import os, re, zipfile;
from .fsGetNormalizedPath import fsGetNormalizedPath;
from cStringIO import StringIO;
from mDebugOutput import cWithDebugOutput;

class cFileSystemItem(cWithDebugOutput):
  def __init__(oSelf, sPath, oParent = None):
    oSelf.fEnterFunctionOutput();
    try:
      oSelf.sPath = fsGetNormalizedPath(sPath, oParent.sPath if oParent else None);
      if oParent:
        sParentPath = fsGetNormalizedPath(oSelf.sPath + os.sep + u"..");
        assert sParentPath == oParent.sPath, \
            "Cannot create a child (path = %s, normalized = %s, parent = %s) for the given parent (path %s)" % \
            (repr(sPath), repr(oSelf.sPath), repr(sParentPath), repr(oParent.sPath));
      oSelf.sName = os.path.basename(oSelf.sPath);
      uDotIndex = oSelf.sName.rfind(".");
      oSelf.sExtension = None if uDotIndex == -1 else oSelf.sName[uDotIndex + 1:];
      
      oSelf.__sWindowsPath = None;
      oSelf.__bWindowsPathSet = False;
      oSelf.__sDOSPath = None;
      oSelf.__bDOSPathSet = False;
      
      oSelf.__oRoot = oParent.oRoot if oParent else None;
      oSelf.__oParent = oParent;
      oSelf.__bParentSet = oParent is not None;
      oSelf.__oPyFile = None;
      oSelf.__oPyZipFile = None;
      oSelf.__doPyFile_by_sRelativePath = {};
      oSelf.__dbWritable_by_sRelativePath = {};
      oSelf.__bWritable = False;
      oSelf.fxExitFunctionOutput(oSelf);
      return;
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  @property
  def oParent(oSelf):
    oSelf.fEnterFunctionOutput();
    try:
      if not oSelf.__bParentSet:
        sParentPath = fsGetNormalizedPath(oSelf.sPath + os.sep + u"..");
        # This will be None for root nodes, where sParentPath == its own path.
        oSelf.__oParent = oSelf.__class__(sParentPath) if sParentPath != oSelf.sPath else None;
        assert oSelf.__oParent is None or sParentPath == oSelf.__oParent.sPath, \
            "Cannot create a parent (path = %s, normalized = %s) for path %s: result is %s" % \
            (repr(oSelf.sPath + os.sep + u".."), repr(sParentPath), repr(oSelf.sPath), repr(oSelf.__oParent.sPath));
        oSelf.__bParentSet = True;
      return oSelf.fxExitFunctionOutput(oSelf.__oParent);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  @property
  def oRoot(oSelf):
    oSelf.fEnterFunctionOutput();
    try:
      if not oSelf.__oRoot:
        oSelf.__oRoot = (
          oSelf.oParent.oRoot if oSelf.oParent
          else oSelf
        );
      return oSelf.fxExitFunctionOutput(oSelf.__oRoot);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def __foGetZipRoot(oSelf, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(bThrowErrors = bThrowErrors);
    try:
      if not oSelf.oParent:
        # If it does not have a parent, it cannot be in a zip file.
        return oSelf.fxExitFunctionOutput(None, "root cannot have a zip root");
      try:
        if os.path.exists(oSelf.sWindowsPath):
          # If it exists in the file system according to the OS, it is not in a .zip
          return oSelf.fxExitFunctionOutput(None, "file exists so cannot have a zip root");
      except:
        if bThrowErrors:
          raise;
      if oSelf.oParent.fbIsValidZipFile(bThrowErrors = bThrowErrors):
        # If its parent is a valid zip file, this is its zip root
        return oSelf.fxExitFunctionOutput(oSelf.oParent, "parent");
      # This item inherits its zip root from its parent.
      oZipRoot = oSelf.oParent.__foGetZipRoot(bThrowErrors = bThrowErrors);
      return oSelf.fxExitFunctionOutput(oZipRoot, "ancestor");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def __del__(oSelf):
    try:
      oSelf.__oPyZipFile.close();
    except Exception:
      pass;
    try:
      oSelf.__oPyFile.close();
    except Exception:
      pass;
    try:
      asOpenWritablePyFiles = oSelf.__dbWritable_by_sRelativePath.keys();
    except Exception:
      pass;
    else:
      assert len(asOpenWritablePyFiles) == 0, \
          "cFileSystemItem: Zip file %s was destroyed while the following writable files were still open: %s" % \
          (oSelf.sPath, ", ".join(asOpenWritablePyFiles));
  
  def fsGetRelativePath(oSelf, xAbsolutePath_or_oOther, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(xAbsolutePath_or_oOther = xAbsolutePath_or_oOther, bThrowErrors = bThrowErrors);
    try:
      sAbsolutePath = xAbsolutePath_or_oOther.sPath if isinstance(xAbsolutePath_or_oOther, cFileSystemItem) \
          else xAbsolutePath_or_oOther;
      if not sAbsolutePath.startswith(oSelf.sPath) or sAbsolutePath[len(oSelf.sPath):len(oSelf.sPath) + 1] not in [os.sep, os.altsep]:
        assert not bThrowErrors, \
              "Cannot get relative path for %s as it is not a descendant of %s" % (sAbsolutePath, oSelf.sPath);
        return oSelf.fxExitFunctionOutput(None, "not a descendant");
      return oSelf.fxExitFunctionOutput(sAbsolutePath[len(oSelf.sPath) + 1:]);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  @property
  def sWindowsPath(oSelf):
    oSelf.fEnterFunctionOutput();
    try:
      if not oSelf.__bWindowsPathSet:
        oSelf.__sWindowsPath = fsGetWindowsPath(oSelf.sPath);
        oSelf.__bWindowsPathSet = True;
      return oSelf.fxExitFunctionOutput(oSelf.__sWindowsPath);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  @property
  def s0DOSPath(oSelf):
    oSelf.fEnterFunctionOutput();
    try:
      if not oSelf.__bDOSPathSet:
        if not oSelf.__foGetZipRoot():
          oSelf.__sDOSPath = fs0GetDOSPath(oSelf.sPath);
        oSelf.__bDOSPathSet = True;
      return oSelf.fxExitFunctionOutput(oSelf.__sDOSPath);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbExists(oSelf, bThrowErrors = False, bParseZipFiles = False):
    oSelf.fEnterFunctionOutput(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles);
    try:
      if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors): return oSelf.fxExitFunctionOutput(True, "open as zip file");
      if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors): return oSelf.fxExitFunctionOutput(True, "open as file");
      try:
        if os.path.exists(oSelf.sWindowsPath):
          return oSelf.fxExitFunctionOutput(True, "file/folder exists");
      except:
        if bThrowErrors:
          raise;
      if bParseZipFiles:
        oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
        if oZipRoot and oZipRoot.__ZipFile_fbContains(oSelf.sPath, bThrowErrors):
          return oSelf.fxExitFunctionOutput(True, "zipped file exists");
      return oSelf.fxExitFunctionOutput(False);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbIsFolder(oSelf, bThrowErrors = False, bParseZipFiles = False):
    oSelf.fEnterFunctionOutput(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles);
    try:
      if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors): return oSelf.fxExitFunctionOutput(False, "open as zip file");
      if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors): return oSelf.fxExitFunctionOutput(False, "open as file");
      try:
        if os.path.isdir(oSelf.sWindowsPath):
          return oSelf.fxExitFunctionOutput(True, "is a folder");
      except:
        if bThrowErrors:
          raise;
      if bParseZipFiles:
        oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
        if oZipRoot and oZipRoot.__ZipFile_fbContainsFolder(oSelf.sPath, bThrowErrors):
          return oSelf.fxExitFunctionOutput(True, "found in file path in zip file");
      return oSelf.fxExitFunctionOutput(False, "not found");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbIsFile(oSelf, bThrowErrors = False, bParseZipFiles = False):
    oSelf.fEnterFunctionOutput(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles);
    try:
      if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors): return oSelf.fxExitFunctionOutput(True, "open as zip file");
      if oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors): return oSelf.fxExitFunctionOutput(True, "open as file");
      try:
        if os.path.isfile(oSelf.sWindowsPath):
          return oSelf.fxExitFunctionOutput(True, "is a file");
      except:
        if bThrowErrors:
          raise;
      if bParseZipFiles:
        oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
        if oZipRoot and oZipRoot.__ZipFile_fbContainsFile(oSelf.sPath, bThrowErrors):
          return oSelf.fxExitFunctionOutput(True, "found in zip file");
      return oSelf.fxExitFunctionOutput(False, "not found");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbIsValidZipFile(oSelf, bThrowErrors = False, bParseZipFiles = False):
    oSelf.fEnterFunctionOutput(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles);
    try:
      if oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors): return oSelf.fxExitFunctionOutput(True, "open as zip file");
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot check if %s is a valid zip file when it is already open as a file!" % oSelf.sPath;
      # If the file exists, try to parse the .zip file to make sure it is valid
      try:
        if os.path.isfile(oSelf.sWindowsPath):
          try:
            zipfile.ZipFile(oSelf.sWindowsPath, "r").close();
          except (IOError, zipfile.BadZipfile) as oError:
            return oSelf.fxExitFunctionOutput(False, "found but not valid");
          else:
            return oSelf.fxExitFunctionOutput(True, "found and valid");
      except:
        if bThrowErrors:
          raise;
      if bParseZipFiles:
        oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
        if oZipRoot:
          oPyFile = oZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWritable = False, bThrowErrors = bThrowErrors);
          if oPyFile:
            try:
              zipfile.ZipFile(oPyFile, "r").close();
            except zipfile.BadZipfile:
              return oSelf.fxExitFunctionOutput(False, "found in zip file but not valid");
            else:
              return oSelf.fxExitFunctionOutput(True, "found in zip file and valid");
            finally:
              assert oZipRoot.__ZipFile_fbClosePyFile(oSelf.sPath, oPyFile, bThrowErrors), \
                  "Cannot close file %s in zip file %s!" % (oSelf.sPath, oZipRoot.sPath);
      return oSelf.fxExitFunctionOutput(False, "not found");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbCreateAsFolder(oSelf, bCreateParents = False, bParseZipFiles = False, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(bCreateParents = bCreateParents, bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it is already open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFile(bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it already exists as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFolder(bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when it already exists!" % oSelf.sPath;
      if oSelf.oParent and not oSelf.oParent.fbExists(bThrowErrors = bThrowErrors):
        assert bCreateParents, \
            "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
        if not oSelf.oParent.fbCreateAsParent(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles):
          return oSelf.fxExitFunctionOutput(False, "cannot create parent");
      if bParseZipFiles and oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors):
        # Zip files cannot have folders, so we will do nothing here. If a file is
        # created in this folder or one of its sub-folders, this folder will 
        # magically start to exist; in effect folders are virtual.
        return oSelf.fxExitFunctionOutput(True, "folder in zip files are virtual");
      else:
        try:
          os.makedirs(oSelf.sWindowsPath);
          if not os.path.isdir(oSelf.sWindowsPath):
            return oSelf.fxExitFunctionOutput(False, "makedirs succeeded but folder does not exist");
        except Exception as oException:
          if bThrowErrors:
            raise;
        return oSelf.fxExitFunctionOutput(False, "Exception: %s" % repr(oException));
      return oSelf.fxExitFunctionOutput(True, "folder created");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def faoGetChildren(oSelf, bMustBeFile = False, bMustBeFolder = False, bMustBeValidZipFile = False, \
      bThrowErrors = False, bParseZipFiles = False):
    oSelf.fEnterFunctionOutput(bMustBeFile = bMustBeFile, bMustBeFolder = bMustBeFolder, \
        bMustBeValidZipFile = bMustBeValidZipFile, bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles);
    try:
      if bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
        asChildNames = oSelf.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
      else:
        oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors) \
            if bParseZipFiles else None;
        if oZipRoot:
          asChildNames = oZipRoot.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
        elif oSelf.fbIsFolder(bThrowErrors = bThrowErrors):
          try:
            asChildNames = os.listdir(oSelf.sWindowsPath)
          except:
            if bThrowErrors:
              raise;
            return oSelf.fxExitFunctionOutput(None, "canot list folder");
        elif bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
          asChildNames = oSelf.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
        else:
          return oSelf.fxExitFunctionOutput(None, "not a folder%s" % (" or zip file" if bParseZipFiles else ""));
      aoChildren = [
        oSelf.__class__(oSelf.sPath + os.sep + sChildName, oSelf)
        for sChildName in sorted(asChildNames)
      ];
      aoChildren = [
        oChild for oChild in aoChildren
        if (
          (not bMustBeFile or oChild.fbIsFile())
          and (not bMustBeFolder or oChild.fbIsFolder())
          and (not bMustBeValidZipFile or oChild.fbIsValidZipFile())
        )
      ];
      return oSelf.fxExitFunctionOutput(aoChildren);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
    
  def foGetChild(oSelf, sChildName, bMustBeFile = False, bMustBeFolder = False, \
      bMustBeValidZipFile = False, bMustExist = False, bThrowErrors = False, bParseZipFiles = False, bFixCase = False):
    oSelf.fEnterFunctionOutput(sChildName = sChildName, bMustBeFile = bMustBeFile, bMustBeFolder = bMustBeFolder,
        bMustBeValidZipFile = bMustBeValidZipFile, bMustExist = bMustExist, bThrowErrors = bThrowErrors,
        bParseZipFiles = bParseZipFiles, bFixCase = bFixCase);
    try:
      assert os.sep not in sChildName and os.altsep not in sChildName, \
          "Cannot create a child %s!" % sChildName;
      if bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
       asChildNames = oSelf.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors);
      else:
        oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors) \
            if bParseZipFiles else None;
        if oZipRoot:
          asChildNames = oZipRoot.__ZipFile_fasGetChildNames(oSelf.sPath, bThrowErrors) \
              if bParseZipFiles else [];
        elif oSelf.fbIsFolder() and bFixCase:
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
      assert oSelf.fsGetRelativePath(oChild.sPath, bThrowErrors = bThrowErrors) == sChildName, \
          "Creating a child %s of %s resulted in a child path %s!" % (sChildName, oSelf.sPath, oChild.sPath);
      assert not bMustBeFile or oChild.fbIsFile(bThrowErrors = bThrowErrors), \
          "Child %s of %s is not a file!" % (sChildName, oSelf.sPath);
      assert not bMustBeFolder or oChild.fbIsFolder(bThrowErrors = bThrowErrors), \
          "Child %s of %s is not a folder!" % (sChildName, oSelf.sPath);
      assert not bMustBeValidZipFile or oChild.fbIsValidZipFile(bThrowErrors = bThrowErrors), \
          "Child %s of %s is not a valid zip file!" % (sChildName, oSelf.sPath);
      assert not bMustExist or oChild.fbExists(bThrowErrors = bThrowErrors), \
          "Child %s of %s does not exist!" % (sChildName, oSelf.sPath);
      return oSelf.fxExitFunctionOutput(oChild);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def faoGetDescendants(oSelf, bMustBeFile = False, bMustBeFolder = False, bMustBeValidZipFile = False,
      bThrowErrors = False, bParseZipFiles = False):
    oSelf.fEnterFunctionOutput(bMustBeFile = bMustBeFile, bMustBeFolder = bMustBeFolder,
        bMustBeValidZipFile = bMustBeValidZipFile, bThrowErrors = bThrowErrors,
        bParseZipFiles = bParseZipFiles);
    try:
      aoDescendants = [];
      aoChildren = oSelf.faoGetChildren(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles);
      if aoChildren is None:
        return oSelf.fxExitFunctionOutput(None, "cannot get list of children");
      for oChild in aoChildren:
        aoDescendants.append(oChild);
        aoDescendants += oChild.faoGetDescendants(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles) or [];
      aoDescendants = [
        oDescendant for oDescendant in aoDescendants
        if (
          (not bMustBeFile or oDescendant.fbIsFile())
          and (not bMustBeFolder or oDescendant.fbIsFolder())
          and (not bMustBeValidZipFile or oDescendant.fbIsValidZipFile())
        )
      ];
      return oSelf.fxExitFunctionOutput(aoDescendants);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def foGetDescendant(oSelf, sDescendantPath, bMustBeFile = False, bMustBeFolder = False, \
      bMustBeValidZipFile = False, bMustExist = False, bThrowErrors = False, bParseZipFiles = False, bFixCase = False):
    oSelf.fEnterFunctionOutput(sDescendantPath = sDescendantPath, bMustBeFile = bMustBeFile, bMustBeFolder = bMustBeFolder,
        bMustBeValidZipFile = bMustBeValidZipFile, bMustExist = bMustExist, bThrowErrors = bThrowErrors,
        bParseZipFiles = bParseZipFiles, bFixCase = bFixCase);
    try:
      sChildName = sDescendantPath.split(os.sep, 1)[0].split(os.altsep, 1)[0];
      assert sChildName, \
          "Cannot get descendant %s of %s because the path is absolute!" % (sDescendantPath, oSelf.sPath);
      sChildDescendantPath = sDescendantPath[len(sChildName) + 1:];
      oChild = oSelf.foGetChild(sChildName, bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles, bFixCase = bFixCase);
      oDescendant = (
        oChild if not sChildDescendantPath else \
        oChild.foGetDescendant(sChildDescendantPath, bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles, bFixCase = bFixCase)
      );
      if oDescendant:
        assert not bMustBeFile or oDescendant.fbIsFile(bThrowErrors = bThrowErrors), \
            "Descendant %s of %s is not a file!" % (sDescendantPath, oSelf.sPath);
        assert not bMustBeFolder or oDescendant.fbIsFolder(bThrowErrors = bThrowErrors), \
            "Descendant %s of %s is not a folder!" % (sDescendantPath, oSelf.sPath);
        assert not bMustBeValidZipFile or oDescendant.fbIsValidZipFile(bThrowErrors = bThrowErrors), \
            "Descendant %s of %s is not a valid zip file!" % (sDescendantPath, oSelf.sPath);
        assert not bMustExist or oDescendant.fbExists(bThrowErrors = bThrowErrors), \
            "Descendant %s of %s does not exist!" % (sDescendantPath, oSelf.sPath);
      return oSelf.fxExitFunctionOutput(oDescendant);
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbSetAsCurrentWorkingDirectory(oSelf, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(bThrowErrors = bThrowErrors);
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot set zip file %s as current working directory!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors) and not oSelf.fbIsFile(bThrowErrors = bThrowErrors), \
          "Cannot set file %s as current working directory!" % oSelf.sPath;
      assert not oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors), \
          "Cannot set folder %s as current working directory if it is inside a zip file!" % oSelf.sPath
      assert oSelf.fbExists(bThrowErrors = bThrowErrors), \
          "Cannot set folder %s as current working directory if it does not exist!" % oSelf.sPath;
      assert oSelf.fbIsFolder(bThrowErrors = bThrowErrors), \
          "Cannot set folder %s as current working directory if it is not a folder!" % oSelf.sPath;
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
      return oSelf.fxExitFunctionOutput(bSuccess, "success" if bSuccess else "failed");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbCreateAsFile(oSelf, sData = "", bCreateParents = False, bParseZipFiles = False, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(sData = sData, bCreateParents = bCreateParents, bParseZipFiles = bParseZipFiles, \
        bThrowErrors = bThrowErrors);
    try:
      assert oSelf.oParent, \
          "Cannot create file %s as a root node!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create file %s when it is already open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFolder(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles), \
          "Cannot create file %s if it already exists as a folder!" % oSelf.sPath;
      assert not oSelf.fbExists(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles), \
          "Cannot create file %s if it already exists!" % oSelf.sPath;
      if not oSelf.oParent.fbExists(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles):
        assert bCreateParents, \
            "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
        if not oSelf.oParent.fbCreateAsParent(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
          return oSelf.fxExitFunctionOutput(False, "Cannot create parent");
      oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
      if oZipRoot:
        if not oZipRoot.__ZipFile_fbCreateFile(oSelf.sPath, sData, bThrowErrors):
          return oSelf.fxExitFunctionOutput(False, "Cannot create file in zip file");
      else:
        try:
          oPyFile = open(oSelf.sWindowsPath, "wb");
          try:
            oPyFile.write(sData);
          finally:
            oPyFile.close();
        except Exception as oException:
          if bThrowErrors:
            raise;
          return oSelf.fxExitFunctionOutput(False, "Exception: %s" % repr(oException));
      return oSelf.fxExitFunctionOutput(True, "success");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbOpenAsFile(oSelf, bWritable = False, bParseZipFiles = False, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(bWritable = bWritable, bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot open file %s twice!" % oSelf.sPath;
      assert oSelf.fbExists(bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it does not exist!" % oSelf.sPath;
      assert oSelf.fbIsFile(bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it is not a file!" % oSelf.sPath;
      oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
      if oZipRoot:
        oSelf.__oPyFile = oZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWritable, bThrowErrors);
        if not oSelf.__oPyFile:
          return oSelf.fxExitFunctionOutput(False, "Cannot open file in zip file");
      else:
        try:
          oSelf.__oPyFile = open(oSelf.sWindowsPath, "wb" if bWritable else "rb");
        except Exception as oException:
          if bThrowErrors:
            raise;
          return oSelf.fxExitFunctionOutput(False, "Exception: %s" % repr(oException));
      oSelf.__bWritable = bWritable;
      return oSelf.fxExitFunctionOutput(True, "success");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fsRead(oSelf, bKeepOpen = None, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(bKeepOpen = bKeepOpen, bThrowErrors = bThrowErrors);
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot read file %s when it is open as a zip file!" % oSelf.sPath;
      # Keep the file open if it is already open, or the special argument is provided.
      # Close or keep the file open depending on the argument, or whether it is currently open if it is not provided.
      bIsOpen = oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors);
      bKeepOpen = bKeepOpen if bKeepOpen is not None else bIsOpen; 
      # Make sure the file is open; leave access rights as is
      if not bIsOpen:
        if not oSelf.fbOpenAsFile(bWritable = oSelf.__bWritable, bThrowErrors = bThrowErrors):
          return oSelf.fxExitFunctionOutput(None, "cannot open file");
      try:
        sData = oSelf.__oPyFile.read();
      except Exception as oException:
        if bThrowErrors:
          raise;
        return oSelf.fxExitFunctionOutput(None, "Exception: %s" % oException);
      finally:
        if not bKeepOpen:
          assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
              "Cannot close %s after reading!" % oSelf.sPath;
      return oSelf.fxExitFunctionOutput(sData, "read %d bytes" % len(sData));
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbWrite(oSelf, sData, bKeepOpen = None, bThrowErrors = False):
    oSelf.fEnterFunctionOutput(sData = sData, bKeepOpen = bKeepOpen, bThrowErrors = bThrowErrors);
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot write file %s when it is open as a zip file!" % oSelf.sPath;
      # Close or keep the file open depending on the argument, or whether it is currently open if it is not provided.
      bIsOpen = oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors);
      bKeepOpen = bKeepOpen if bKeepOpen is not None else bIsOpen; 
      # Make sure the file is open; and writable
      if not bIsOpen:
        if not oSelf.fbOpenAsFile(bWritable = True, bThrowErrors = bThrowErrors):
          return oSelf.fxExitFunctionOutput(False, "cannot open file");
      try:
        oSelf.__oPyFile.write(sData);
      except Exception as oException:
        if bThrowErrors:
          raise;
        return oSelf.fxExitFunctionOutput(False, "Exception: %s" % oException);
      finally:
        if not bKeepOpen:
          assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
              "Cannot close %s after writing!" % oSelf.sPath;
      return oSelf.fxExitFunctionOutput(True, "success");
    except Exception as oException:
      oSelf.fxRaiseExceptionOutput(oException);
      raise;
  
  def fbCreateAsZipFile(oSelf, bKeepOpen = False, bCreateParents = False, bParseZipFiles = False, bThrowErrors = False):
    assert oSelf.oParent, \
        "Cannot create zip file %s as a root node!" % oSelf.sPath;
    assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create zip file %s when it is already open as a zip file!" % oSelf.sPath;
    assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
        "Cannot create zip file %s when it is already open as a file!" % oSelf.sPath;
    assert not oSelf.fbExists(bThrowErrors = bThrowErrors), \
        "Cannot create zip file %s if it already exists!" % oSelf.sPath;
    if not oSelf.oParent.fbExists(bThrowErrors = bThrowErrors):
      assert bCreateParents, \
          "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
      if not oSelf.oParent.fbCreateAsParent(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles):
        return False;
    oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if oZipRoot:
      oSelf.__oPyFile = oZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWriteable = True, bThrowErrors = bThrowErrors);
      if not oSelf.__oPyFile: return False;
    else:
      # Open/create the file as writable and truncate it if it already existed.
      try:
        oSelf.__oPyFile = open(oSelf.sWindowsPath, "wb");
      except:
        if bThrowErrors:
          raise;
        return False;
    oSelf.__bWriteable = True;
    try:
      oSelf.__oPyFile.write("");
      oSelf.__oPyZipFile = zipfile.ZipFile(oSelf.__oPyFile, "w");
    except:
      if oZipRoot:
        assert oZipRoot.__ZipFile_fbClosePyFile(oSelf.sPath, oSelf.__oPyFile, bThrowErrors), \
            "Cannot close zip file %s in zip file %s" % (oSelf.sPath, oZipRoot.sPath);
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close %s!" % oSelf.sPath;
      if bThrowErrors:
        raise;
      return False;
    if not bKeepOpen:
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close zip file %s after creating!" % oSelf.sPath;
    return True;
  
  def fbOpenAsZipFile(oSelf, bWritable = False, bThrowErrors = False):
    assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot open zip file %s twice!" % oSelf.sPath;
    assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
        "Cannot open zip file %s when it is already open as a file!" % oSelf.sPath;
    assert oSelf.fbExists(bThrowErrors = bThrowErrors), \
        "Cannot open zip file %s if it does not exist!" % oSelf.sPath;
    assert oSelf.fbIsFile(bThrowErrors = bThrowErrors), \
        "Cannot open zip file %s when it is not a file!" % oSelf.sPath;
    oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
    if oZipRoot:
      oSelf.__oPyFile = oZipRoot.__ZipFile_foOpenPyFile(oSelf.sPath, bWriteable, bThrowErrors);
      if not oSelf.__oPyFile: return False;
    else:
      try:
        oSelf.__oPyFile = open(oSelf.sWindowsPath, "wb" if bWritable else "rb");
      except:
        if bThrowErrors:
          raise;
        return False;
    try:
      oSelf.__oPyZipFile = zipfile.ZipFile(oSelf.__oPyFile, "w" if bWritable else "r", zipfile.ZIP_DEFLATED);
    except:
      if oZipRoot:
        assert oZipRoot.__ZipFile_fbClosePyFile(oSelf.sPath, oSelf.__oPyFile, bThrowErrors), \
            "Cannot close zip file %s in zip file %s" % (oSelf.sPath, oZipRoot.sPath);
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close %s!" % oSelf.sPath;
      if bThrowErrors:
        raise;
      return False;
    oSelf.__bWritable = bWritable;
    return True;
  
  def fbCreateAsParent(oSelf, bThrowErrors = False, bParseZipFiles = False):
    bIsZipFile = oSelf.sExtension and oSelf.sExtension.lower() == "zip";
    sCreateAsType = "zip file" if bIsZipFile else "folder";
    assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create %s %s when it is already open as a zip file!" % (sCreateAsType, oSelf.sPath);
    assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
        "Cannot create %s %s when it is already open as a file!" % (sCreateAsType, oSelf.sPath);
    assert not oSelf.fbIsFile(bThrowErrors = bThrowErrors), \
        "Cannot create %s %s when it already exists as a file!" % (sCreateAsType, oSelf.sPath);
    assert not oSelf.fbIsFolder(bThrowErrors = bThrowErrors), \
        "Cannot create %s %s when it already exists as a folder!" % (sCreateAsType, oSelf.sPath);
    assert not oSelf.fbExists(bThrowErrors = bThrowErrors), \
        "Cannot create %s %s if it already exists!" % (sCreateAsType, oSelf.sPath);
    if not oSelf.oParent.fbExists(bThrowErrors = bThrowErrors) \
        and not oSelf.oParent.fbCreateAsParent(bThrowErrors = bThrowErrors, bParseZipFiles = bParseZipFiles):
      return False;
    return (
      oSelf.fbCreateAsZipFile(bThrowErrors = bThrowErrors) if bIsZipFile and bParseZipFiles else
      oSelf.fbCreateAsFolder(bThrowErrors = bThrowErrors)
    );
  
  def fbIsOpenAsFile(oSelf, bThrowErrors = False):
    return oSelf.__oPyFile is not None and not oSelf.__oPyZipFile is not None;
  def fbIsOpenAsZipFile(oSelf, bThrowErrors = False):
    return oSelf.__oPyZipFile is not None;
  def fbIsOpen(oSelf, bThrowErrors = False):
    return oSelf.__oPyFile is not None;
  
  def fbClose(oSelf, bThrowErrors = False):
    assert oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors) or oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
        "Cannot close %s when it is not open!" % oSelf.sPath;
    if oSelf.__oPyZipFile:
      try:
        oSelf.__oPyZipFile.close();
      except:
        if bThrowErrors:
          raise;
        return False;
      oSelf.__oPyZipFile = None;
    if oSelf.__oPyFile:
      oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
      if oZipRoot:
        assert oZipRoot.__ZipFile_fbClosePyFile(oSelf.sPath, oSelf.__oPyFile, bThrowErrors), \
            "Cannot close zip file %s in zip file %s" % (oSelf.sPath, oZipRoot.sPath);
      try:
        oSelf.__oPyFile.close();
      except:
        if bThrowErrors:
          raise;
        return False;
      oSelf.__oPyFile = None;
    oSelf.__bWritable = False;
    return True;
  
  def fbRename(oSelf, sNewName, bThrowErrors = False):
    assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
        "Cannot rename %s when it is open as a file!" % oSelf.sPath;
    assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot rename %s when it is open as a zip file!" % oSelf.sPath;
    oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
    assert not oZipRoot, \
        "Renaming is not implemented within zip files!";
    oNewItem = oSelf.oParent.foGetChild(sNewName, bThrowErrors = bThrowErrors);
    try:
      os.rename(oSelf.sWindowsPath, oNewItem.sWindowsPath);
    except:
      if bThrowErrors:
        raise;
      return False;
    if not oNewItem.fbExists(bThrowErrors = bThrowErrors):
      return False;
    oSelf.sPath = oNewItem.sPath;
    oSelf.sName = oNewItem.sName;
    oSelf.sExtension = oNewItem.sExtension;
    oSelf.__sWindowsPath = oNewItem.__sWindowsPath;
    oSelf.__bWindowsPathSet = oNewItem.__bWindowsPathSet;
    oSelf.__sDOSPath = oNewItem.__sDOSPath;
    oSelf.__bDOSPathSet = oNewItem.__bDOSPathSet;
    return True;
  
  def fbDeleteDescendants(oSelf, bClose = False, bThrowErrors = False):
    if bClose:
      if not oSelf.fbClose(bThrowErrors = bThrowErrors):
        return False;
    else:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot delete %s when it is open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot delete %s when it is open as a file!" % oSelf.sPath;
    assert not oSelf.fbIsFile(bThrowErrors = bThrowErrors), \
        "Cannot delete descendants of %s when it is a file!" % oSelf.sPath;
    aoChildren = oSelf.faoGetChildren(bThrowErrors = bThrowErrors);
    if aoChildren is None:
      return False;
    for oChild in aoChildren:
      if not oChild.fbDelete(bThrowErrors = bThrowErrors):
        return False;
    return True;
  
  def fbDelete(oSelf, bClose = False, bThrowErrors = False):
    if bClose:
      if not oSelf.fbClose(bThrowErrors = bThrowErrors):
        return False;
    else:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot delete %s when it is open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot delete %s when it is open as a file!" % oSelf.sPath;
    oZipRoot = oSelf.__foGetZipRoot(bThrowErrors = bThrowErrors);
    assert not oZipRoot, \
        "Deleting is not implemented within zip files!";
    # Handle descendants if any
    if oSelf.fbIsFile(bThrowErrors = bThrowErrors):
      try:
        os.remove(oSelf.sWindowsPath);
      except:
        if bThrowErrors:
          raise;
        return False;
      if oSelf.fbExists(bThrowErrors = bThrowErrors):
        return False;
    else:
      if not oSelf.fbDeleteDescendants(bThrowErrors = bThrowErrors):
        return False;
      try:
        os.rmdir(oSelf.sWindowsPath);
      except:
        if bThrowErrors:
          raise;
        return False;
      if oSelf.fbExists(bThrowErrors = bThrowErrors):
        return False;
    return True;

  def foCreateChildFolder(oSelf, sChildName, bKeepOpen = False, bCreateParents = False, bThrowErrors = False):
    assert os.sep not in sChildName and os.altsep not in sChildName and sChildName != "..", \
        "Cannot create a child folder %s!" % sChildName;
    assert not oSelf.fbIsFile(bThrowErrors = bThrowErrors) or oSelf.fbIsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create a child folder %s of %s when it exists as a file!" % (sChildName, oSelf.sPath);
    assert oSelf.fbIsFolder(bThrowErrors = bThrowErrors) or oSelf.fbIsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create a child folder %s of %s when it is not a folder or a zip file!" % (sChildName, oSelf.sPath);
    oChild = oSelf.__class__(os.path.join(oSelf.sPath, sChildName), oSelf);
    if not oChild.fbCreateAsFolder(bKeepOpen = bKeepOpen, bCreateParents = bCreateParents, bThrowErrors = bThrowErrors):
      return None;
    return oChild;
    
  def foCreateChildFile(oSelf, sChildName, bKeepOpen = False, bCreateParents = False, bThrowErrors = False):
    assert os.sep not in sChildName and os.altsep not in sChildName and sChildName != "..", \
        "Cannot create a child file %s!" % sChildName;
    assert not oSelf.fbIsFile(bThrowErrors = bThrowErrors) or oSelf.fbIsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create a child file %s of %s when it exists as a file!" % (sChildName, oSelf.sPath);
    assert oSelf.fbIsFolder(bThrowErrors = bThrowErrors) or oSelf.fbIsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create a child file %s of %s when it is not a folder or a zip file!" % (sChildName, oSelf.sPath);
    oChild = oSelf.__class__(os.path.join(oSelf.sPath, sChildName), oSelf);
    if not oChild.fbCreateAsFile(bKeepOpen = bKeepOpen, bCreateParents = bCreateParents, bThrowErrors = bThrowErrors):
      return None;
    return oChild;

  def foCreateChildZipFile(oSelf, sChildName, bKeepOpen = False, bCreateParents = False, bThrowErrors = False):
    assert os.sep not in sChildName and os.altsep not in sChildName and sChildName != "..", \
        "Cannot create a child zip file %s!" % sChildName;
    assert not oSelf.fbIsFile(bThrowErrors = bThrowErrors) or oSelf.fbIsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create a child zip file %s of %s when it exists as a file!" % (sChildName, oSelf.sPath);
    assert oSelf.fbIsFolder(bThrowErrors = bThrowErrors) or oSelf.fbIsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot create a child zip file %s of %s when it is not a folder or a zip file!" % (sChildName, oSelf.sPath);
    oChild = oSelf.__class__(os.path.join(oSelf.sPath, sChildName), oSelf);
    if not oChild.fbCreateAsZipFile(bKeepOpen = bKeepOpen, bCreateParents = bCreateParents, bThrowErrors = bThrowErrors):
      return None;
    return oChild;
  
  def __ZipFile_fbContains(oSelf, sPath, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot check if %s contains %s if it cannot be opened!" % (oSelf.sPath, sPath);
    try:
      sRelativePath = oSelf.fsGetRelativePath(sPath, bThrowErrors = bThrowErrors);
      for sZippedFilePath in oSelf.__oPyZipFile.namelist():
        sZippedFilePath = sZippedFilePath.replace(os.altsep, os.sep);
        if sZippedFilePath.startswith(sRelativePath):
          if sZippedFilePath[len(sRelativePath):len(sRelativePath) + 1] in ["", os.sep]:
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
      sPathHeader = oSelf.fsGetRelativePath(sPath, bThrowErrors = bThrowErrors) + os.sep;
      for sZippedFilePath in oSelf.__oPyZipFile.namelist():
        sZippedFilePath = sZippedFilePath.replace(os.altsep, os.sep);
        if sZippedFilePath.startswith(sPathHeader):
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
      sRelativePath = oSelf.fsGetRelativePath(sPath, bThrowErrors = bThrowErrors);
      for sZippedFilePath in oSelf.__oPyZipFile.namelist():
        sZippedFilePath = sZippedFilePath.replace(os.altsep, os.sep);
        if sZippedFilePath == sRelativePath:
          return True;
      return False;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close %s" % oSelf.sPath;
  
  def __ZipFile_fbCreateFile(oSelf, sPath, sData, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bWritable = True, bThrowErrors = bThrowErrors), \
          "Cannot check if %s contains a file %s if it cannot be opened!" % (oSelf.sPath, sPath);
    try:
      sRelativePath = oSelf.fsGetRelativePath(sPath, bThrowErrors = bThrowErrors);
      try:
        oSelf.__oPyZipFile.writestr(sRelativePath, sData);
      except:
        if bThrowErrors:
          raise;
        return False;
      return True;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close %s" % oSelf.sPath;
  
  def __ZipFile_foOpenPyFile(oSelf, sPath, bWritable, bThrowErrors):
    sRelativePath = oSelf.fsGetRelativePath(sPath, bThrowErrors = bThrowErrors);
    assert sRelativePath not in oSelf.__doPyFile_by_sRelativePath, \
        "Cannot open file %s in zip file %s if it is already open!" % (sPath, oSelf.sPath);
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
    try:
      for sRealZippedFilePath in oSelf.__oPyZipFile.namelist():
        sZippedFilePath = sRealZippedFilePath.replace(os.altsep, os.sep);
        if sZippedFilePath == sRelativePath:
          sData = oSelf.__oPyZipFile.read(sRealZippedFilePath);
          oPyFile = StringIO(sData);
          oSelf.__doPyFile_by_sRelativePath[sRelativePath] = oPyFile;
          oSelf.__dbWritable_by_sRelativePath[sRelativePath] = bWritable;
          return oPyFile;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close zip file %s!" % oSelf.sPath;
    raise AssertionError("Cannot file %s in zip file %s!" % (sPath, oSelf.sPath));
  
  def __ZipFile_fbClosePyFile(oSelf, sPath, oPyFile, bThrowErrors):
    sRelativePath = oSelf.fsGetRelativePath(sPath, bThrowErrors = bThrowErrors);
    assert sRelativePath in oSelf.__doPyFile_by_sRelativePath and sRelativePath in oSelf.__dbWritable_by_sRelativePath, \
        "Cannot close file %s in zip file %s if it is not open!" % (sRelativePath, oSelf.sPath);
    assert oPyFile == oSelf.__doPyFile_by_sRelativePath[sRelativePath], \
        "Internal inconsistency!";
    bWritable = oSelf.__dbWritable_by_sRelativePath[sRelativePath];
    if bWritable:
      bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
      if bMustBeClosed:
        assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
            "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
      try:
        # We assume writable files have been modifed and need to be saved in the zip file.
        try:
          oPyFile.seek(0);
          sData = oPyFile.read();
          oSelf.__oPyZipFile.writestr(sRelativePath, sData);
        except:
          if bThrowErrors:
            raise;
          return False;
      finally:
        if bMustBeClosed:
          assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
              "Cannot close zip file %s!" % oSelf.sPath;
    del oSelf.__doPyFile_by_sRelativePath[sRelativePath];
    del oSelf.__dbWritable_by_sRelativePath[sRelativePath];
    return True;
  
  def __ZipFile_fasGetChildNames(oSelf, sPath, bThrowErrors):
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
    try:
      sPathHeader = oSelf.fsGetRelativePath(sPath + os.sep, bThrowErrors = bThrowErrors);
      asChildNames = [];
      for sZippedFilePath in oSelf.__oPyZipFile.namelist():
        sZippedFilePath = sZippedFilePath.replace(os.altsep, os.sep);
        if sZippedFilePath.startswith(sPathHeader):
          sRelativeZippedFilePath = sZippedFilePath[len(sPathHeader):];
          sChildName = sRelativeZippedFilePath.split(os.sep, 1)[0];
          if sChildName not in asChildNames:
            asChildNames.append(sChildName);
      return asChildNames;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close zip file %s!" % oSelf.sPath;

from .fsGetWindowsPath import fsGetWindowsPath;
from .fs0GetDOSPath import fs0GetDOSPath;

