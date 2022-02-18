def cFileSystemItem_fbDeleteDescendants(oSelf, bClose, bParseZipFile, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    try:
      if not bClose:
        assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
            "Cannot delete %s when it is open as a zip file!" % oSelf.sPath;
        assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
            "Cannot delete %s when it is open as a file!" % oSelf.sPath;
      assert not oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot delete descendants of %s when it is a file!" % oSelf.sPath;
    except AssertionError:
      if bThrowErrors:
        raise;
      return False;
  if bClose and not oSelf.fbClose(bThrowErrors = bThrowErrors):
    return False;
  a0oChildren = oSelf.fa0oGetChildren(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
  if a0oChildren is None:
    return False;
  for oChild in a0oChildren:
    if not oChild.fbDelete(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors):
      return False;
  return True;
