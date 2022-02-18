def cFileSystemItem_fbZipFileContainsDescendantFile(oSelf, sPath, bThrowErrors):
  bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
  if bMustBeClosed:
    assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot check if %s contains a file %s if it cannot be opened!" % (oSelf.sPath, sPath);
  try:
    sZipInternalPath = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace("\\", "/");
    return sZipInternalPath in oSelf._cFileSystemItem__fdoGetCachedPyZipInfo_by_sZipInternalPath().keys();
  finally:
    if bMustBeClosed:
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close %s" % oSelf.sPath;