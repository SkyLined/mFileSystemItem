import os;

def cFileSystemItem_fo0GetDescendant(oSelf, sDescendantRelativePath, bFixCase, bParseZipFiles, bThrowErrors, bSanityChecks):
  if bSanityChecks:
    pass;
  # Get the first part: up until the folder separator
  sChildName = sDescendantRelativePath.split(os.sep, 1)[0];
  if os.altsep:
    # If there is an alternative folder separator, apply that too:
    sChildName = sChildName.split(os.altsep, 1)[0];
  assert sChildName, \
      "Cannot get descendant %s of %s because the path is absolute!" % (sDescendantRelativePath, oSelf.sPath);
  sChildDescendantPath = sDescendantRelativePath[len(sChildName) + 1:];
  o0Child = oSelf.fo0GetChild(
    sChildName,
    bFixCase = bFixCase,
    bParseZipFiles = bParseZipFiles,
    bThrowErrors = bThrowErrors,
  );
  if o0Child is None:
    return None;
  o0Descendant = (
    o0Child if not sChildDescendantPath else \
    o0Child.fo0GetDescendant(
      sChildDescendantPath,
      bFixCase = bFixCase,
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = bThrowErrors,
    )
  );
  return o0Descendant;