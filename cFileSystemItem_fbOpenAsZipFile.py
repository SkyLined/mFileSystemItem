import zipfile;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbOpenAsZipFile(oSelf, bWritable, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      # Note that bParseZipFiles applies to its parents.
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot open zip file %s twice!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot open zip file %s when it is already open as a file!" % oSelf.sPath;
      assert oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot open zip file %s when it %s!" % (
            oSelf.sPath,
            "is not a file" if oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
                else "does not exist",
          );
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
  if o0ZipRoot:
    oSelf._cFileSystemItem__o0PyFile = o0ZipRoot._cFileSystemItem__fo0OpenZipFileDescendantAsPyFile(oSelf.sPath, bWritable, bThrowErrors);
    if not oSelf._cFileSystemItem__o0PyFile:
      return False;
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = True;
    oSelf._cFileSystemItem__bWasReadOnlyBeforeOpen = False;
    oSelf._cFileSystemItem__bWasHiddenBeforeOpen = False;
  else:
    oSelf._cFileSystemItem__fRemoveAccessLimitingAttributesBeforeOperation();
    try:
      oSelf._cFileSystemItem__o0PyFile = open(oSelf.sWindowsPath, "a+b" if bWritable else "rb");
    except:
      oSelf._cFileSystemItem__fReapplyAccessLimitingAttributesAfterOperation();
      if bThrowErrors:
        raise;
      return False;
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = False;
  try:
    oSelf._cFileSystemItem__o0PyZipFile = zipfile.ZipFile(
      oSelf._cFileSystemItem__o0PyFile,
      "a" if bWritable else "r",
      zipfile.ZIP_DEFLATED,
    );
    oSelf._cFileSystemItem__do0PyZipInfo_by_sZipInternalPath = None;
    fShowDebugOutput("Opened for %s." % ("appending" if bWritable else "reading"));
    oSelf._cFileSystemItem__bWritable = bWritable;
    return True;
  except:
    # This should always succeed so it will always throw errors if it does not
    oSelf.fClose();
    if bThrowErrors:
      raise;
    return False;