import os;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fu0GetSize(oSelf, bThrowErrors):
  try:
    uSize = os.path.getsize(oSelf.sWindowsPath);
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("cannot get info from the file system");
    return None;
  fShowDebugOutput("got info from the file system");
  return uSize;