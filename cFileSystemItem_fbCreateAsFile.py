try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbCreateAsFile(oSelf, sbData, bCreateParents, bParseZipFiles, bKeepOpen, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      assert oSelf.o0Parent, \
          "Cannot create file %s as a root node!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create file %s when it is already open as a zip file!" % oSelf.sPath;
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create file %s when it is already open as a file!" % oSelf.sPath;
      assert not oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create file %s if it already exists%s!" % (
            oSelf.sPath,
            " as a folder" if oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
                else ""
          );
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
  if o0ZipRoot:
    o0PyFile = o0ZipRoot._cFileSystemItem__fo0CreateZipFileDescendant(oSelf.sPath, sbData, bThrowErrors);
    if o0PyFile is None:
      fShowDebugOutput("Cannot create file in zip file");
      return False;
    if not bKeepOpen:
      assert o0ZipRoot._cFileSystemItem__fbCloseZipFileDescendantPyFile(oSelf.sPath, o0PyFile, bThrowErrors), \
          "Cannot close %s" % oSelf.sPath;
    else:
      oSelf._cFileSystemItem__o0PyFile = o0PyFile;
      oSelf._cFileSystemItem__bPyFileIsInsideZipFile = True;
      oSelf._cFileSystemItem__bWasReadOnlyBeforeOpen = False;
      oSelf._cFileSystemItem__bWasHiddenBeforeOpen = False;
      oSelf._cFileSystemItem__bWritable = True;
    return True;
  if not oSelf.o0Parent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
    if not bCreateParents:
      assert not bThrowErrors, \
          "Cannot create file %s when its parent does not exist!" % oSelf.sPath;
      return False;
    if not oSelf.o0Parent.fbCreateAsParent(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      fShowDebugOutput("Cannot create parent");
      return False;
  try:
    oSelf._cFileSystemItem__o0PyFile = open(oSelf.sWindowsPath, "wb");
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = False;
    oSelf._cFileSystemItem__bWasReadOnlyBeforeOpen = False;
    oSelf._cFileSystemItem__bWasHiddenBeforeOpen = False;
    oSelf._cFileSystemItem__bWritable = True;
    try:
      oSelf._cFileSystemItem__o0PyFile.write(sbData);
    finally:
      if not bKeepOpen:
        oSelf._cFileSystemItem__o0PyFile.close();
        oSelf._cFileSystemItem__o0PyFile = None;
        oSelf._cFileSystemItem__bPyFileIsInsideZipFile = False;
        oSelf._cFileSystemItem__bWritable = False;
    return True;
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % repr(oException));
    return False;