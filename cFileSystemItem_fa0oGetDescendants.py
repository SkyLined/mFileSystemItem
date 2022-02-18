try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fa0oGetDescendants(oSelf, bParseZipFiles, bParseDescendantZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    pass;
  aoDescendants = [];
  a0oChildren = oSelf.fa0oGetChildren(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors);
  if a0oChildren is None:
    fShowDebugOutput("cannot get list of children");
    return None;
  for oChild in a0oChildren:
    aoDescendants.append(oChild);
    if (
      oChild.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
      or (
        bParseDescendantZipFiles
        and oChild.fbIsValidZipFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
      )
    ):
      # oSelf or its parents can only be zip files if bParseZipFiles was true. If oSelf nor any of its
      # parents were zip files, setting bParseZipFiles has no affect. So we can use bParseZipFiles = true
      aoDescendants += oChild.fa0oGetDescendants(
        bThrowErrors = bThrowErrors,
        bParseZipFiles = bParseZipFiles,
        bParseDescendantZipFiles = bParseDescendantZipFiles,
      ) or [];
  return aoDescendants;