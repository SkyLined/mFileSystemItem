import os;

def cFileSystemItem_fo0GetChild(oSelf, sChildName, bParseZipFiles, bFixCase, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      assert os.sep not in sChildName and (os.altsep is None or os.altsep not in sChildName), \
          "Cannot create a child %s!" % sChildName;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  if bParseZipFiles and oSelf.fbIsValidZipFile(bThrowErrors = bThrowErrors):
   asChildNames = oSelf._cFileSystemItem__fasGetChildNamesOfZipFileDescendant(oSelf.sPath, bThrowErrors);
  else:
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if o0ZipRoot:
      asChildNames = o0ZipRoot._cFileSystemItem__fasGetChildNamesOfZipFileDescendant(oSelf.sPath, bThrowErrors) \
          if bParseZipFiles else [];
    elif (
      oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
      and bFixCase
    ):
      try:
        asChildNames = os.listdir(oSelf.sWindowsPath);
      except:
        if bThrowErrors:
          raise;
        asChildNames = [];
    else:
      asChildNames = [];
  # Look for an existing child that has the same name but different casing
  sLowerChildName = sChildName.lower();
  for sRealChildName in asChildNames:
    if sRealChildName.lower() == sLowerChildName:
      # Found one: use that name instead.
      sChildName = sRealChildName;
      break;
  oChild = oSelf.__class__(oSelf.sPath + os.sep + sChildName, oSelf);
  assert oSelf.fsGetRelativePathTo(oChild, bThrowErrors = bThrowErrors) == sChildName, \
      "Creating a child %s of %s resulted in a child path %s!" % (sChildName, oSelf.sPath, oChild.sPath);
  return oChild;