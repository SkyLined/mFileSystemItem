try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fsb0Read(oSelf, bThrowErrors):
  oSelf._cFileSystemItem__fRemoveAccessLimitingAttributesBeforeOperation(bMustBeWritable = False);
  try:
    with open(oSelf.sWindowsPath, "rb") as oPyFile:
      return oPyFile.read();
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % oException);
    return None;
  finally:
    oSelf._cFileSystemItem__fReapplyAccessLimitingAttributesAfterOperation();
