try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbCreateAsFile(oSelf, sbData, bCreateParents, bThrowErrors):
  try:
    assert oSelf.o0Parent, \
        "Cannot create file %s because it has no parent to create it in!" % oSelf.sPath;
    assert not oSelf.fbExists(bThrowErrors = bThrowErrors), \
        "Cannot create file %s if it already exists%s!" % (
          oSelf.sPath,
          " as a folder" if oSelf.fbIsFolder(bThrowErrors = bThrowErrors)
              else ""
        );
  except AssertionError:
    if bThrowErrors:
      raise;
    return False;
  if not oSelf.o0Parent.fbExists(bThrowErrors = bThrowErrors):
    if not bCreateParents:
      assert not bThrowErrors, \
          "Cannot create file %s when its parent does not exist!" % oSelf.sPath;
      return False;
    if not oSelf.o0Parent.fbCreateAsParent(bThrowErrors = bThrowErrors):
      return False;
  try:
    with open(oSelf.sWindowsPath, "wb") as oPyFile:
      oPyFile.write(sbData);
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % oException);
    return False;
  else:
    return True;
