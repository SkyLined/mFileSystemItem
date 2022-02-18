import os;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbCreateAsFolder(oSelf, bCreateParents, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
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
      oSelf.o0Parent
      and not oSelf.o0Parent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
    ):
      if not bCreateParents:
        assert not bThrowErrors, \
            "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
        return False;
      if not oSelf.o0Parent.fbCreateAsParent(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        fShowDebugOutput("cannot create parent");
        return False;
    try:
      os.makedirs(oSelf.sWindowsPath);
    except Exception as oException:
      if bThrowErrors:
        raise;
      fShowDebugOutput("cannot create folder(s): %s" % repr(oException));
      return False;
    if not os.path.isdir(oSelf.sWindowsPath):
      fShowDebugOutput("makedirs succeeded but folder does not exist");
      return False;
  fShowDebugOutput("folder created");
  return True;