import os;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fa0oGetChildren(oSelf, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    pass;
  if bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
    asChildNames = oSelf._cFileSystemItem__fasGetChildNamesOfZipFileDescendant(oSelf.sPath, bThrowErrors);
  else:
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if o0ZipRoot:
      asChildNames = o0ZipRoot._cFileSystemItem__fasGetChildNamesOfZipFileDescendant(oSelf.sPath, bThrowErrors);
    elif oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      try:
        asChildNames = os.listdir(oSelf.sWindowsPath)
      except Exception as oException:
        if bThrowErrors:
          raise;
        fShowDebugOutput("cannot list folder: %s" % oException);
        return None;
    elif bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
      asChildNames = oSelf._cFileSystemItem__fasGetChildNamesOfZipFileDescendant(oSelf.sPath, bThrowErrors);
    else:
      fShowDebugOutput("not a folder%s" % (" or zip file" if bParseZipFiles else ""));
      return None;
  return [
    oSelf.__class__(oSelf.sPath + os.sep + sChildName, oSelf)
    for sChildName in sorted(asChildNames)
  ];