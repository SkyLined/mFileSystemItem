import os;

def cFileSystemItem_fbRename(oSelf, sNewName, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
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
  assert oSelf.o0Parent, \
      "Cannot rename root node";
  o0NewItem = oSelf.o0Parent.fo0GetChild(
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
  oSelf._cFileSystemItem__sWindowsPath = o0NewItem._cFileSystemItem__sWindowsPath;
  oSelf._cFileSystemItem__bWindowsPathSet = o0NewItem._cFileSystemItem__bWindowsPathSet;
  oSelf._cFileSystemItem_cFileSystemItem__sDOSPath = o0NewItem._cFileSystemItem__sDOSPath;
  oSelf._cFileSystemItem__bDOSPathSet = o0NewItem._cFileSystemItem__bDOSPathSet;
  return True;