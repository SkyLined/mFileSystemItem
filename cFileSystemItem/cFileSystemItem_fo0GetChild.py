import os;

def cFileSystemItem_fo0GetChild(oSelf, sChildName, bFixCase, bThrowErrors):
  try:
    assert os.sep not in sChildName and (os.altsep is None or os.altsep not in sChildName), \
        "Cannot create a child %s!" % sChildName;
  except AssertionError:
    if bThrowErrors:
      raise;
    return None;
  if bFixCase and oSelf.fbIsFolder(bThrowErrors = bThrowErrors):
    try:
      asChildNames = os.listdir(oSelf.sWindowsPath);
    except:
      if bThrowErrors:
        raise;
    else:
      # Look for an existing child that has the same name but different casing
      sLowerChildName = sChildName.lower();
      for sRealChildName in asChildNames:
        if sRealChildName.lower() == sLowerChildName:
          # Found one: use that name instead.
          sChildName = sRealChildName;
          break;
  oChild = oSelf.__class__(oSelf.sPath + os.sep + sChildName, oSelf);
  assert oSelf.fsGetRelativePathTo(oChild, bThrowErrors = False) == sChildName, \
      "Creating a child %s of %s resulted in a child %s that has relative path %s!" % (
        sChildName,
        oSelf.sPath,
        oChild.sPath,
        oSelf.fsGetRelativePathTo(oChild, bThrowErrors = False),
      );
  return oChild;