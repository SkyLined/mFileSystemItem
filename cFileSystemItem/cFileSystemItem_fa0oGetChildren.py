import os;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fa0oGetChildren(oSelf, bThrowErrors):
  try:
    asChildNames = os.listdir(oSelf.sWindowsPath) if os.path.isdir(oSelf.sWindowsPath) else [];
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("cannot list folder: %s" % oException);
    return None;
  return [
    oSelf.__class__(oSelf.sPath + os.sep + sChildName, oSelf)
    for sChildName in sorted(asChildNames)
  ];