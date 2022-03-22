import os;

def cFileSystemItem_fbRename(oSelf, sNewName, bThrowErrors):
  assert oSelf.o0Parent, \
      "Cannot rename root node";
  o0NewItem = oSelf.o0Parent.fo0GetChild(
    sNewName,
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
  if not o0NewItem.fbExists(bThrowErrors = bThrowErrors):
    return False;
  oSelf.sPath = o0NewItem.sPath;
  oSelf.sName = o0NewItem.sName;
  oSelf.s0Extension = o0NewItem.s0Extension;
  oSelf._cFileSystemItem__sWindowsPath = o0NewItem._cFileSystemItem__sWindowsPath;
  oSelf._cFileSystemItem__bWindowsPathSet = o0NewItem._cFileSystemItem__bWindowsPathSet;
  oSelf._cFileSystemItem_cFileSystemItem__sDOSPath = o0NewItem._cFileSystemItem__sDOSPath;
  oSelf._cFileSystemItem__bDOSPathSet = o0NewItem._cFileSystemItem__bDOSPathSet;
  return True;