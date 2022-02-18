import os;

def cFileSystemItem_fbSetAsCurrentWorkingDirectory(oSelf, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      # CWD cannot be a zip file so not bParseZipFiles argument exists.
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot set zip file %s as current working directory!" % oSelf.sPath;
      assert (
        not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors)
        and not oSelf.fbIsFile(bParseZipFiles = False, bThrowErrors = bThrowErrors)
      ), \
          "Cannot set file %s as current working directory!" % oSelf.sPath;
      assert oSelf.fbIsFolder(bParseZipFiles = False, bThrowErrors = bThrowErrors), \
          "Cannot set folder %s as current working directory if it %s!" % (
            oSelf.sPath,
            "is not a folder" if oSelf.fbExists(bParseZipFiles = False, bThrowErrors = bThrowErrors)
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