import os;

def cFileSystemItem_fbMove(oSelf, oNewItem, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
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
  oSelf._cFileSystemItem__sWindowsPath = oNewItem._cFileSystemItem__sWindowsPath;
  oSelf._cFileSystemItem__bWindowsPathSet = oNewItem._cFileSystemItem__bWindowsPathSet;
  oSelf._cFileSystemItem__sDOSPath = oNewItem._cFileSystemItem__sDOSPath;
  oSelf._cFileSystemItem__bDOSPathSet = oNewItem._cFileSystemItem__bDOSPathSet;
  return True;