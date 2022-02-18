def cFileSystemItem_fbCreateAsParent(oSelf, bParseZipFiles, bThrowErrors, bSanityChecks):
  bIsZipFile = oSelf.s0Extension and oSelf.s0Extension.lower() == "zip";
  sCreateAsType = "zip file" if bIsZipFile else "folder";
  if bSanityChecks:
    try:
      assert not oSelf.fbIsOpenAsZipFile(bThrowErrors = bThrowErrors), \
          "Cannot create %s %s when it is already open as a zip file!" % (sCreateAsType, oSelf.sPath);
      assert not oSelf.fbIsOpenAsFile(bThrowErrors = bThrowErrors), \
          "Cannot create %s %s when it is already open as a file!" % (sCreateAsType, oSelf.sPath);
      assert not oSelf.fbIsFile(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
          "Cannot create %s %s when it already exists as a file!" % (sCreateAsType, oSelf.sPath);
    except AssertionError:
      if bThrowErrors:
        raise;
  if not bIsZipFile and bParseZipFiles:
    o0ZipRoot = oSelf.fo0GetZipRoot(bThrowErrors = bThrowErrors) if bParseZipFiles else None;
    if o0ZipRoot:
      # Folders cannot be stored within a zip file; only files can be stored with a relative
      # path that contain folder names. So, if we are asked to create a parent folder it must
      # be for such a file that has this parent folder in its path. This means no action is
      # needed: the folder will magically exists once the file is created. Except that we do
      # need to create the zip file that contains this folder if it does not exists. If the
      # file exists, we should check it already exists:
      if not o0ZipRoot.fbExists(bParseZipFiles = True, bThrowErrors = bThrowErrors):
        return o0ZipRoot.fbCreateAsZipFile(
          bCreateParents = True,
          bParseZipFiles = bParseZipFiles,
          bThrowErrors = bThrowErrors,
        );
      assert o0ZipRoot.fbIsValidZipFile(bParseZipFiles = True, bThrowErrors = bThrowErrors), \
          "Cannot create folder %s when %s is not a valid zip file!" % (oSelf.sPath, o0ZipRoot.sPath);
      return True;
  assert not oSelf.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors), \
      "Cannot create %s %s if it already exists as a %s!" % (
        sCreateAsType,
        oSelf.sPath,
        "folder" if oSelf.fbIsFolder(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
            else "file",
      );
  assert oSelf.o0Parent, \
      "Cannot create %s %s as it is a root node!" % (sCreateAsType, oSelf.sPath);
  if (
    not oSelf.o0Parent.fbExists(bParseZipFiles = bParseZipFiles, bThrowErrors = bThrowErrors)
    and not oSelf.o0Parent.fbCreateAsParent(
      bParseZipFiles = bParseZipFiles,
      bThrowErrors = bThrowErrors,
    )
  ):
    return False;
  if bIsZipFile and bParseZipFiles:
    return oSelf.fbCreateAsZipFile(
      bCreateParents = True,
      bParseZipFiles = True,
      bThrowErrors = bThrowErrors,
    );
  return oSelf.fbCreateAsFolder(
    bCreateParents = True,
    bParseZipFiles = bParseZipFiles,
    bThrowErrors = bThrowErrors,
  );
