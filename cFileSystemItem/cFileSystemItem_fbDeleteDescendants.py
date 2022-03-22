def cFileSystemItem_fbDeleteDescendants(oSelf, bThrowErrors):
  for oChild in oSelf.fa0oGetChildren(bThrowErrors = bThrowErrors):
    if not oChild.fbDelete(bThrowErrors = bThrowErrors):
      return False;
  return True;
