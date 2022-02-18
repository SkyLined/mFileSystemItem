import os;

def cFileSystemItem_fbDelete(oSelf, bClose, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      if not bClose:
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
  if bClose and not oSelf.fbClose(bThrowErrors = bThrowErrors):
    return False;
  # Handle descendants if any
  bIsFolder = oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
  if bIsFolder and not oSelf.fbDeleteDescendants(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
    return False;
  # Remive hidden/read-only attributes;
  oSelf._cFileSystemItem__fRemoveAccessLimitingAttributesBeforeOperation();
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
