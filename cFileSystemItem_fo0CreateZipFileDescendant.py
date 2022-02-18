try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fo0CreateZipFileDescendant(oSelf, sPath, sbData, bThrowErrors):
  sZipInternalPath = oSelf.fsGetRelativePathTo(
    sPath,
    bThrowErrors = bThrowErrors,
  ).replace("\\", "/");
  o0PyFile = oSelf._cFileSystemItem__fo0OpenZipFileDescendantAsPyFile(sPath, True, bThrowErrors);
  if not o0PyFile:
    fShowDebugOutput("zip file descendant cannot be opened");
    return None;
  try:
    o0PyFile.write(sbData);
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("cannot write: %s" % oException);
    return None;
  return o0PyFile;
