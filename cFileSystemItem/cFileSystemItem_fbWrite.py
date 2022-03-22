try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fbWrite(oSelf, sbData, bAppend, bCreateParents, bThrowErrors):
  if not oSelf.fbIsFile(bThrowErrors = bThrowErrors):
    assert not bAppend, \
        "Cannot append to %s: the file does not exist" % oSelf.sPath;
    return oSelf._cFileSystemItem__fbCreateAsFile(sbData, bCreateParents, bThrowErrors);
  oSelf._cFileSystemItem__fRemoveAccessLimitingAttributesBeforeOperation(bMustBeWritable = True);
  try:
    with open(oSelf.sWindowsPath, "a+b" if bAppend else "wb") as oPyFile:
      oPyFile.write(sbData);
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("Exception: %s" % oException);
    return False;
  else:
    return True;
  finally:
    oSelf._cFileSystemItem__fReapplyAccessLimitingAttributesAfterOperation();
