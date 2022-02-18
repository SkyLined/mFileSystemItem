def cFileSystemItem_fu0GetCompressedSize(oSelf, bThrowErrors, bSanityChecks): # bParseZipFiles == True is implied
  if bSanityChecks:
    pass;
  o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
  if not o0ZipRoot:
    assert not bThrowErrors, \
        "Cannot get compressed size of %s because it is not in a zip file" % oSelf.sPath;
    fShowDebugOutput("not found inside its zip file ancestor");
    return None;
  u0Size = o0ZipRoot._cFileSystemItem__fu0GetCompressedSizeOfZipFileDescendant(oSelf.sPath, bThrowErrors);
  return u0Size;