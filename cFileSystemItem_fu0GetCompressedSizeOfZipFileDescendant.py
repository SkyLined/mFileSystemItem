def cFileSystemItem_fu0GetCompressedSizeOfZipFileDescendant(oSelf, sPath, bThrowErrors):
  sZipInternalPath = oSelf.fsGetRelativePathTo(
    sPath,
    bThrowErrors = bThrowErrors,
  ).replace("\\", "/");
  if oSelf.dbWritable_by_sZipInternalPath.get(sZipInternalPath):
    assert not bThrowErrors, \
        "Cannot get compressed sized of a file that is open for writing; please close it first!";
    return None;
  o0PyZipInfo = oSelf.fo0GetZipInfoForZipFileDescendant(sPath, bThrowErrors);
  return o0PyZipInfo.compress_size if o0PyZipInfo else None;

