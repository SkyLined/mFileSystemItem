from io import BytesIO;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fo0OpenZipFileDescendantAsPyFile(oSelf, sPath, bWritable, bThrowErrors):
  sZipInternalPath = oSelf.fsGetRelativePathTo(
    sPath,
    bThrowErrors = bThrowErrors,
  ).replace("\\", "/");
  assert sZipInternalPath not in oSelf._cFileSystemItem__doPyFile_by_sZipInternalPath, \
      "Cannot open file %s in zip file %s if it is already open!" % (sPath, oSelf.sPath);
  bMustBeClosed = not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors);
  if bMustBeClosed:
    if not oSelf.fbOpenAsZipFile(bThrowErrors = bThrowErrors):
      fShowDebugOutput("zip file cannot be opened");
      return None;
  try:
    bFileExistsInZipFile = sZipInternalPath in oSelf._cFileSystemItem__fdoGetCachedPyZipInfo_by_sZipInternalPath();
    if bFileExistsInZipFile:
      sbData = oSelf._cFileSystemItem__o0PyZipFile.read(sZipInternalPath);
      oPyFile = BytesIO();
      oPyFile.write(sbData);
      oPyFile.seek(0);
      fShowDebugOutput("opened file for %s in zip file" % ("reading" if not bWritable else "writing"));
    else:
      assert bWritable, \
          "Cannot open file %s in zip file %s for reading if it does not exist!" % (sPath, oSelf.sPath);
      oPyFile = BytesIO();
      fShowDebugOutput("created virtual file in zip file");
    oSelf._cFileSystemItem__doPyFile_by_sZipInternalPath[sZipInternalPath] = oPyFile;
    oSelf._cFileSystemItem__dbWritable_by_sZipInternalPath[sZipInternalPath] = bWritable;
    return oPyFile;
  finally:
    if bMustBeClosed:
      assert oSelf.fbClose(bThrowErrors = bThrowErrors), \
          "Cannot close zip file %s!" % oSelf.sPath;
  raise AssertionError("Cannot file %s in zip file %s!" % (sPath, oSelf.sPath));
