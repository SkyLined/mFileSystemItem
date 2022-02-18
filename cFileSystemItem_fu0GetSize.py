import os;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fu0GetSize(oSelf, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    pass;
  if bParseZipFiles:
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors);
    if o0ZipRoot:
      u0Size = o0ZipRoot._cFileSystemItem__fu0GetSizeOfZipFileDescendant(oSelf.sPath, bThrowErrors);
      fShowDebugOutput("got info from its zip file ancestor %s" % o0ZipRoot.sPath);
      return u0Size;
  try:
    uSize = os.path.getsize(oSelf.sWindowsPath);
  except Exception as oException:
    if bThrowErrors:
      raise;
    fShowDebugOutput("cannot get info from the file system");
    return None;
  fShowDebugOutput("got info from the file system");
  return uSize;