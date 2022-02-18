try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbOpenAsFile(oSelf, bWritable, bAppend, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot open file %s twice!" % oSelf.sPath;
      assert oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot open file %s when it %s!" % (
            oSelf.sPath,
            "is not a file" if oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
                else "does not exist"
          );
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
  if o0ZipRoot:
    oSelf._cFileSystemItem__o0PyFile = o0ZipRoot._cFileSystemItem__fo0OpenZipFileDescendantAsPyFile(oSelf.sPath, bWritable, bThrowErrors);
    if not oSelf._cFileSystemItem__o0PyFile:
      fShowDebugOutput("Cannot open file in zip file");
      return False;
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = True;
    oSelf._cFileSystemItem__bWasReadOnlyBeforeOpen = False;
    oSelf._cFileSystemItem__bWasHiddenBeforeOpen = False;
  else:
    oSelf._cFileSystemItem__fRemoveAccessLimitingAttributesBeforeOperation();
    try:
      oSelf._cFileSystemItem__o0PyFile = open(oSelf.sWindowsPath, ("a+b" if bAppend else "wb") if bWritable else "rb");
    except Exception as oException:
      oSelf._cFileSystemItem__fReapplyAccessLimitingAttributesAfterOperation();
      if bThrowErrors:
        raise;
      fShowDebugOutput("Exception: %s" % repr(oException));
      return False;
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = False;
  oSelf._cFileSystemItem__bWritable = bWritable;
  return True;