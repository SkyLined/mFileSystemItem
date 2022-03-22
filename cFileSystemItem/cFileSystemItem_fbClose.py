try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbClose(oSelf, oPyFile, bThrowErrors):
  try:
    oPyFile.close();
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % repr(oException));
    return False;
  else:
    return True;
  finally:
    oSelf._cFileSystemItem__fReapplyAccessLimitingAttributesAfterOperation();
