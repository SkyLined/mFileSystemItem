import zipfile;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbCloseZipFileDescendantPyFile(oSelf, sPath, oPyFile, bThrowErrors):
  sZipInternalPath = oSelf.fsGetRelativePathTo(
    sPath,
    bThrowErrors = bThrowErrors,
  ).replace("\\", "/");
  bWritable = oSelf._cFileSystemItem__dbWritable_by_sZipInternalPath[sZipInternalPath];
  if bWritable:
    bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
    if bMustBeClosed:
      assert oSelf.fbOpenAsZipFile(bWritable = bWritable, bThrowErrors = bThrowErrors), \
          "Cannot get files list of zip file %s if it cannot be opened!" % oSelf.sPath;
    doPyZipInfo_by_sZipInternalPath = oSelf._cFileSystemItem__fdoGetCachedPyZipInfo_by_sZipInternalPath();
    assert sZipInternalPath not in doPyZipInfo_by_sZipInternalPath, \
        "Cannot create/overwrite existing file %s in zip file %s!" % (sPath, oSelf.sPath);
    assert sZipInternalPath in oSelf._cFileSystemItem__doPyFile_by_sZipInternalPath \
        and sZipInternalPath in oSelf._cFileSystemItem__dbWritable_by_sZipInternalPath, \
        "Cannot close file %s in zip file %s if it is not open!" % (sPath, oSelf.sPath);
    assert oPyFile == oSelf._cFileSystemItem__doPyFile_by_sZipInternalPath[sZipInternalPath], \
        "Internal inconsistency!";
    try:
      # We assume writable files have been modified and need to be saved in the zip file.
      try:
        oPyFile.seek(0);
        sbData = oPyFile.read();
        fShowDebugOutput("Writing %d bytes (%s) to %s..." % (
          len(sbData),
          sbData if len(sbData) < 10 else repr(sbData[:7] + b"..."),
          sZipInternalPath)
        );
        oSelf._cFileSystemItem__o0PyZipFile.writestr(sZipInternalPath, sbData, zipfile.ZIP_DEFLATED);
      except:
        # We want to catch any exceptions related to writing the data here, and
        # handle them if `bThrowErrors` is False. However, we want to still throw
        # any unexpected exceptions.
        raise;
        if bThrowErrors:
          raise;
        return False;
      oPyZipInfo = oSelf._cFileSystemItem__o0PyZipFile.getinfo(sZipInternalPath);
      doPyZipInfo_by_sZipInternalPath[sZipInternalPath] = oPyZipInfo;
    finally:
      if bMustBeClosed:
        assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
            "Cannot close zip file %s!" % oSelf.sPath;
  del oSelf._cFileSystemItem__doPyFile_by_sZipInternalPath[sZipInternalPath];
  del oSelf._cFileSystemItem__dbWritable_by_sZipInternalPath[sZipInternalPath];
  return True;
