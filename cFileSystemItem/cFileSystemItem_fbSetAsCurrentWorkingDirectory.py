import os;

from ..fsGetWindowsPath import fsGetWindowsPath;

def cFileSystemItem_fbSetAsCurrentWorkingDirectory(oSelf, bThrowErrors):
  try:
    assert oSelf.fbIsFolder(bThrowErrors = bThrowErrors), \
        "Cannot set folder %s as current working directory because it %s!" % (
          oSelf.sPath,
          "is not a folder" if oSelf.fbExists(bThrowErrors = bThrowErrors)
            else "does not exists"
        );
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