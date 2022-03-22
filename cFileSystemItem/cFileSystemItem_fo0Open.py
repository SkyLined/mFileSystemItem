try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fo0Open(oSelf, bWritable, bAppend, bThrowErrors):
  oSelf._cFileSystemItem__fRemoveAccessLimitingAttributesBeforeOperation(bMustBeWritable = bWritable);
  try:
    return open(oSelf.sWindowsPath, ("a+b" if bAppend else "wb") if bWritable else "rb");
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % repr(oException));
    return None;
