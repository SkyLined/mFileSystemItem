try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbClose(oSelf, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      assert (
        oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors)
        or oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors)
      ), \
          "Cannot close %s when it is not open!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  if oSelf._cFileSystemItem__o0PyZipFile:
    try:
      oSelf._cFileSystemItem__o0PyZipFile.close();
    except:
      if bThrowErrors:
        raise;
      return False;
    oSelf._cFileSystemItem__o0PyZipFile = None;
    oSelf._cFileSystemItem__do0PyZipInfo_by_sZipInternalPath = None;
    fShowDebugOutput("Closed zip file");
  if oSelf._cFileSystemItem__o0PyFile:
    if oSelf._cFileSystemItem__bPyFileIsInsideZipFile:
      o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
      assert o0ZipRoot, \
          "Cannot find zip root for file %s" % (oSelf.sPath,);
      assert o0ZipRoot._cFileSystemItem__fbCloseZipFileDescendantPyFile(oSelf.sPath, oSelf._cFileSystemItem__o0PyFile, bThrowErrors), \
          "Cannot close zip file %s in zip file %s" % (oSelf.sPath, o0ZipRoot.sPath);
    else:
      try:
        oSelf._cFileSystemItem__o0PyFile.close();
      except:
        if bThrowErrors:
          raise;
        return False;
    oSelf._cFileSystemItem__fReapplyAccessLimitingAttributesAfterOperation();
    oSelf._cFileSystemItem__o0PyFile = None;
    oSelf._cFileSystemItem__bPyFileIsInsideZipFile = False;
    fShowDebugOutput("Closed file");
  oSelf._cFileSystemItem__bWritable = False;
  return True;