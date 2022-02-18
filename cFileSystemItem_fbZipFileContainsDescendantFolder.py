def cFileSystemItem_fbZipFileContainsDescendantFolder(oSelf, sPath, bThrowErrors):
  bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
  if bMustBeClosed:
    assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot check if %s contains a folder %s if it cannot be opened!" % (oSelf.sPath, sPath);
  try:
    sWantedZipInternalPathHeader = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace("\\", "/") + "/";
    for sZipInternalPath in oSelf._cFileSystemItem__fdoGetCachedPyZipInfo_by_sZipInternalPath().keys():
      if sZipInternalPath.startswith(sWantedZipInternalPathHeader):
        return True;
    return False;
  finally:
    if bMustBeClosed:
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close %s" % oSelf.sPath;