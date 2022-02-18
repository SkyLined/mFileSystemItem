def cFileSystemItem_fo0GetZipInfoForZipFileDescendant(oSelf, sPath, bThrowErrors):
  bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
  if bMustBeClosed:
    assert oSelf.fbOpenAsZipFile(bWritable = False, bThrowErrors = bThrowErrors), \
        "Cannot check if %s contains a file %s if it cannot be opened!" % (oSelf.sPath, sPath);
  try:
    sZipInternalPath = oSelf.fsGetRelativePathTo(
      sPath,
      bThrowErrors = bThrowErrors,
    ).replace("\\", "/");
    o0PyZipInfo = oSelf._cFileSystemItem__fdoGetCachedPyZipInfo_by_sZipInternalPath().get(sZipInternalPath);
    if not o0PyZipInfo:
      assert not bThrowErrors, \
        "Cannot get information for non-existing file %s in zip file %s!" % (sPath, oSelf.sPath);
    return o0PyZipInfo;
  finally:
    if bMustBeClosed:
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close %s" % oSelf.sPath;
