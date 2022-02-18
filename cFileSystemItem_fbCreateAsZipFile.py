import zipfile;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbCreateAsZipFile(oSelf, bKeepOpen, bCreateParents, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      assert oSelf.o0Parent, \
          "Cannot create zip file %s as a root node!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create zip file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create zip file %s when it is already open as a file!" % oSelf.sPath;
      assert not oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create zip file %s if it already exists!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
  if o0ZipRoot:
    oSelf._cFileSystemItem__o0PyFile = o0ZipRoot._cFileSystemItem__fo0OpenZipFileDescendantAsPyFile(oSelf.sPath, bWritable = True, bThrowErrors = bThrowErrors);
    if not oSelf._cFileSystemItem__o0PyFile:
      fShowDebugOutput("Cannot create file as zip file");
      return False;
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = True;
  else:
    if not oSelf.o0Parent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      if not bCreateParents:
        assert not bThrowErrors, \
            "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
        return False;
      if not oSelf.o0Parent.fbCreateAsParent(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
        return False;
    # Open/create the file as writable and truncate it if it already existed.
    try:
      oSelf._cFileSystemItem__o0PyFile = open(oSelf.sWindowsPath, "wb");
    except:
      if bThrowErrors:
        raise;
      return False;
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = False;
  oSelf._cFileSystemItem__bWasReadOnlyBeforeOpen = False;
  oSelf._cFileSystemItem__bWasHiddenBeforeOpen = False;
  oSelf._cFileSystemItem__bWritable = True;
  try:
    oSelf._cFileSystemItem__o0PyFile.write(b"");
    oSelf._cFileSystemItem__o0PyZipFile = zipfile.ZipFile(oSelf._cFileSystemItem__o0PyFile, "w");
    oSelf._cFileSystemItem__do0PyZipInfo_by_sZipInternalPath = {};
  except:
    # This should always succeed so it will always throw errors if it does not
    oSelf.fClose();
    if bThrowErrors:
      raise;
    return False;
  if not bKeepOpen:
    # This should always succeed so it will always throw errors if it does not
    oSelf.fClose();
  fShowDebugOutput("Created zip file%s%s..." % (
    " inside another zip file" if oSelf._cFileSystemItem__bPyFileIsInsideZipFile else "",
    " and left it open" if bKeepOpen else "",
  ));
  return True;
