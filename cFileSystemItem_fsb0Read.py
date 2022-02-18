try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fsb0Read(oSelf, bKeepOpen, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    # Note that we assume that the caller wants us to parse zip files, unlike most other functions!
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot read file %s when it is open as a zip file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  # Keep the file open if it is already open, or the special argument is provided.
  # Close or keep the file open depending on the argument, or whether it is currently open if it is not provided.
  bIsOpen = oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors);
  bKeepOpen = bKeepOpen if bKeepOpen is not None else bIsOpen; 
  # Make sure the file is open
  if not bIsOpen:
    if not oSelf.fbOpenAsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      fShowDebugOutput("cannot open file");
      return None;
  try:
    sbData = oSelf._cFileSystemItem__o0PyFile.read();
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % oException);
    return None;
  finally:
    if not bKeepOpen:
      # This must always succeed, so it will always throw errors if it does not.
      oSelf.fClose();
  return sbData;