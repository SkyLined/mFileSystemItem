import os;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbCreateAsFolder(oSelf, bCreateParents, bThrowErrors):
  try:
    assert oSelf.o0Parent, \
        "Cannot create folder %s because it has no parent to create it in!" % oSelf.sPath;
    assert not oSelf.fbIsFile(bThrowErrors = bThrowErrors), \
        "Cannot create folder %s when it already exists as a file!" % oSelf.sPath;
    assert not oSelf.fbIsFolder(bThrowErrors = bThrowErrors), \
        "Cannot create folder %s when it already exists!" % oSelf.sPath;
  except AssertionError:
    if bThrowErrors:
      raise;
    return False;
  if not oSelf.o0Parent.fbExists(bThrowErrors = bThrowErrors):
    if not bCreateParents:
      assert not bThrowErrors, \
          "Cannot create folder %s when its parent does not exist!" % oSelf.sPath;
      return False;
    if not oSelf.o0Parent.fbCreateAsParent(bThrowErrors = bThrowErrors):
      return False;
  try:
    os.makedirs(oSelf.sWindowsPath);
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("cannot create folder(s): %s" % repr(oException));
    return False;
  if not os.path.isdir(oSelf.sWindowsPath):
    fShowDebugOutput("makedirs succeeded but folder does not exist");
    return False;
  fShowDebugOutput("folder created");
  return True;