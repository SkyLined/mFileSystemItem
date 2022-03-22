try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

def cFileSystemItem_fa0oGetDescendants(oSelf, bThrowErrors):
  a0oChildren = oSelf.fa0oGetChildren(bThrowErrors = bThrowErrors);
  if a0oChildren is None:
    return None;
  aoDescendants = [];
  for oChild in a0oChildren:
    aoDescendants.append(oChild);
    aoDescendants.extend(
      oChild.fa0oGetDescendants(bThrowErrors = bThrowErrors) or []
    );
  return aoDescendants;