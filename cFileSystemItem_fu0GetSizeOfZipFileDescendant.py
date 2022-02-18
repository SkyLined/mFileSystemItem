def cFileSystemItem_fu0GetSizeOfZipFileDescendant(oSelf, sPath, bThrowErrors):
  sZipInternalPath = oSelf.fsGetRelativePathTo(
    sPath,
    bThrowErrors = bThrowErrors,
  ).replace("\\", "/");
  if oSelf._cFileSystemItem__dbWritable_by_sZipInternalPath.get(sZipInternalPath):
    # If it is open for writing, we're always writing at the end of the file.
    # Since `tell()` returns the offet from the start of the file where writing will happen, it returns the number
    # of bytes in the file:
    oPyFile = oSelf._cFileSystemItem__doPyFile_by_sZipInternalPath[sZipInternalPath];
    return oPyFile.tell();
  o0PyZipInfo = oSelf.fo0GetZipInfoForZipFileDescendant(sPath, bThrowErrors);
  return o0PyZipInfo.file_size if o0PyZipInfo else None;
