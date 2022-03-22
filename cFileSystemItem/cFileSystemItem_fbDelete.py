import os;

def cFileSystemItem_fbDelete(oSelf, bThrowErrors):
  # Handle descendants if any
  bIsFolder = oSelf.fbIsFolder(bThrowErrors = bThrowErrors);
  if bIsFolder:
    if not oSelf.fbDeleteDescendants(bThrowErrors = bThrowErrors):
      return False;
  elif not oSelf.fbIsFile(bThrowErrors = bThrowErrors):
    assert not bThrowErrors, \
        "Cannot delete %s: it does not exist" % oSelf.sPath;
  # Remove hidden/read-only attributes;
  oSelf._cFileSystemItem__fRemoveAccessLimitingAttributesBeforeOperation(bMustBeWritable = True);
  # Delete folder or file
  try:
    if bIsFolder:
      os.rmdir(oSelf.sWindowsPath);
    else:
      os.remove(oSelf.sWindowsPath);
  except:
    if bThrowErrors:
      raise;
    return False;
  # No need to restore hidden/read-only attributes
  # Make sure it no longer exists
  if oSelf.fbExists(bThrowErrors = bThrowErrors):
    if bThrowErrors:
      raise AssertionError("Folder %s exists after being removed!?" % oSelf.sPath);
    return False;
  return True;
