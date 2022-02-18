def cFileSystemItem_fdoGetCachedPyZipInfo_by_sZipInternalPath(oSelf):
  if oSelf._cFileSystemItem__do0PyZipInfo_by_sZipInternalPath is None:
    oSelf._cFileSystemItem__do0PyZipInfo_by_sZipInternalPath = dict([
      (oPyZipInfo.filename, oPyZipInfo)
      for oPyZipInfo in oSelf._cFileSystemItem__o0PyZipFile.infolist()
    ]);
  return oSelf._cFileSystemItem__do0PyZipInfo_by_sZipInternalPath;
