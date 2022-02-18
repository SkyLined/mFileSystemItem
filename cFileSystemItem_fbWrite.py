try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbWrite(oSelf, sbData, bAppend, bCreateParents, bKeepOpen, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      # Note that we assume that the caller wants us to parse zip files, unlike most other functions!
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot write file %s when it is open as a zip file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  # Close or keep the file open depending on the argument, or whether it is currently open if it is not provided.
  bIsOpen = oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors);
  bKeepOpen = bKeepOpen if bKeepOpen is not None else bIsOpen; 
  # Make sure the file is open and writable
  if not bIsOpen:
    if not oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      if not oSelf._cFileSystemItem__fbCreateAsFile(sbData, bCreateParents, bParseZipFiles, bKeepOpen, bThrowErrors, bSanityChecks = True):
        fShowDebugOutput("cannot create file");
        return False;
      return True;
    if not oSelf.fbOpenAsFile(
      bWritable = True,
      bAppend = bAppend,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = bThrowErrors,
    ):
      fShowDebugOutput("cannot open file");
      return False;
  try:
    oSelf._cFileSystemItem__o0PyFile.write(sbData);
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % oException);
    return False;
  finally:
    if not bKeepOpen:
      # This should alwyas succeed so it will always throw errors if it does not.
      oSelf.fClose();
  return True;
