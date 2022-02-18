def cFileSystemItem_fasGetChildNamesOfZipFileDescendant(oSelf, sPath, bThrowErrors):
  bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
  if bMustBeClosed:
    assert oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors), \
        "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
  try:
    sWantedZipInternalPathHeader = (
      "" if sPath == oSelf.sPath
      else oSelf.fsGetRelativePathTo(
        sPath,
        bThrowErrors = bThrowErrors,
      ).replace("\\", "/") + "/"
    );
    uMinLength = len(sWantedZipInternalPathHeader); # Used to speed things up
    asChildNames = [];
    for sZipInternalPath in oSelf._cFileSystemItem__fdoGetCachedPyZipInfo_by_sZipInternalPath().keys():
      if len(sZipInternalPath) > uMinLength and sZipInternalPath.startswith(sWantedZipInternalPathHeader):
        sZipInternalRelativePath = sZipInternalPath[len(sWantedZipInternalPathHeader):];
        sChildName = sZipInternalRelativePath.split("/", 1)[0];
        if sChildName not in asChildNames:
          asChildNames.append(sChildName);
    return asChildNames;
  finally:
    if bMustBeClosed:
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close zip file %s!" % oSelf.sPath;
