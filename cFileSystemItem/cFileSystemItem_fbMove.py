import os;

def cFileSystemItem_fbMove(oSelf, oNewItem, bThrowErrors):
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
  oSelf.s0Extension = oNewItem.s0Extension;
  oSelf._cFileSystemItem__sWindowsPath = oNewItem._cFileSystemItem__sWindowsPath;
  oSelf._cFileSystemItem__bWindowsPathSet = oNewItem._cFileSystemItem__bWindowsPathSet;
  oSelf._cFileSystemItem__sDOSPath = oNewItem._cFileSystemItem__sDOSPath;
  oSelf._cFileSystemItem__bDOSPathSet = oNewItem._cFileSystemItem__bDOSPathSet;
  return True;