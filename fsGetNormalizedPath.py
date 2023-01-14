import os, re;

sCWD = os.getcwd();
bWindowsOS = os.name == "nt";
bDebugOutput = False;

def fsJoinPathSections(*tsPathSections):
  sPath = os.path.join(*tsPathSections);
  if len(sPath) > 1 and sPath.endswith(os.sep) and (
    not bWindowsOS or len(sPath) != 3 or sPath[1] != ":"
  ): # remove trailing slash except for "X:\\"
    return sPath[:-1];
  return sPath;

def fsNormalizePathSection(sPathSection):
  if sPathSection == "": return sPathSection;
  assert ":" not in sPathSection, \
    "Path section %s is invalid" % repr(sPathSection);
  sNormalizedPathSection = os.path.normpath(sPathSection);
  if sNormalizedPathSection == ".":
    return "";
  assert (
    not sNormalizedPathSection.startswith(os.sep)
    and not sNormalizedPathSection.startswith("..")
  ), \
      "Path section %s is normalized as %s, which indicates %s" % (
        sPathSection, sNormalizedPathSection,
        "an absolute path" if sNormalizedPathSection.startswith(os.sep) else "directory traversal",
      );
  return sNormalizedPathSection;

rUNCPath = re.compile(
  r"\A"
  r"(?:"                  # either {
    r"\\\\\?\\UNC\\"       #   "\\?\UNC\"
  r"|"                    # } or {
    r"\\\\\?\\"            #   "\\?\"
  r"|"                    # } or {
    r"\\\\"               #   "\\"
  r")"                    # }
  r"([A-Za-z][0-9A-Za-z\-\._]*)"  # * server name (DNS, WINS, IP)
  r"[\\\/]"               # "\" or "/"
  r"([A-Za-z][0-9A-Za-z\-\._]*)"  # * share name
  r"(?:\\(.*))?"          # optional { "\" * path }
  r"\Z"
);
rDriveLetterAndPath = re.compile(
  r"\A"
  r"(?:\\\\\?\\)?"         # optional { "\\?\" }
  r"([A-Za-z]:)"          # * { drive letter ":" }
  r"([\\\/])*"            # * optional { "\" or "/" any number of times }
  r"(.*)"                 # * optional { path }
  r"\Z"
);
def fsGetNormalizedPath(sPath = sCWD, s0RelativePath = None):
  assert isinstance(sPath, str), \
      "sPath must be a string, not %s" % repr(sPath);
  assert s0RelativePath is None or isinstance(s0RelativePath, str), \
      "sBasePath must be a string, not %s" % repr(s0RelativePath);
  if bDebugOutput:
    print("sPath = %s" % repr(sPath));
    if s0RelativePath:
      print("s0RelativePath = %s" % repr(s0RelativePath));
  sNormalizedPathAddition = fsNormalizePathSection(s0RelativePath or "");
  if bWindowsOS:
    if sPath.startswith("\\\\.\\"): # Physical drive
      raise NotImplementedError();
    # Check for UNC path first
    oUNCPathMatch = rUNCPath.match(sPath);
    if oUNCPathMatch:
      sServerName, sShareName, s0PathInShare = oUNCPathMatch.groups();
      sNormalizedPathInShare = fsNormalizePathSection(s0PathInShare or "")
      if bDebugOutput:
        print("  => UNC PATH");
        print("    Server:    %s" % sServerName);
        print("    Share:     %s" % sShareName);
        print("    Path:      %s" % sNormalizedPathInShare);
        print("    Addition:  %s" % sNormalizedPathAddition);
      return "\\\\%s" % fsJoinPathSections(sServerName, sShareName, sNormalizedPathInShare, sNormalizedPathAddition);
    # Check for drive letter and path:
    oDriveLetterAndPathMatch = rDriveLetterAndPath.match(sPath)
    if oDriveLetterAndPathMatch:
      sDrive, sAbsolute, sPathOnDrive  = oDriveLetterAndPathMatch.groups();
      sNormalizedPathOnDrive = fsNormalizePathSection(sPathOnDrive);
      if sAbsolute:
        sNormalizedPath = fsJoinPathSections(sDrive + "\\", sNormalizedPathOnDrive, sNormalizedPathAddition);
        if bDebugOutput:
          print("  => ABS DRIVE:PATH");
          print("    Drive:       %s" % sDrive);
          print("    Path:        %s" % sNormalizedPathOnDrive);
          print("    Addition:    %s" % sNormalizedPathAddition);
          print("  * Normalized:  %s" % sNormalizedPath);
        return sNormalizedPath;
      sDriveCWDAbsolutePath = os.path.abspath(sDrive);
      sNormalizedPath = fsJoinPathSections(sDriveCWDAbsolutePath, sNormalizedPathOnDrive, sNormalizedPathAddition);
      if bDebugOutput:
        print("  => REL DRIVE:PATH");
        print("    Drive:     %s" % sDrive);
        print("    CWD:       %s" % sDriveCWDAbsolutePath);
        print("    Path:      %s" % sNormalizedPathOnDrive);
        print("    Addition:  %s" % sNormalizedPathAddition);
        print("  * Normalized:  %s" % sNormalizedPath);
      return sNormalizedPath;
    # path only
    if sPath.startswith(os.sep) or sPath.startswith(os.altsep):
      sDrive = sCWD[:2];
      sNormalizedAbsolutePath  = fsNormalizePathSection(sPath[1:]);
      sNormalizedPath = fsJoinPathSections(sDrive + "\\", sNormalizedAbsolutePath, sNormalizedPathAddition);
      if bDebugOutput:
        print("  => ABS PATH");
        print("    Drive:     %s" % sDrive);
        print("    Path:      %s" % sNormalizedPath);
        print("    Addition:  %s" % sNormalizedPathAddition);
        print("  * Normalized:  %s" % sNormalizedPath);
      return sNormalizedPath;
    sNormalizedRelativePath = fsNormalizePathSection(sPath);
    sNormalizedPath = fsJoinPathSections(sCWD, sNormalizedRelativePath, sNormalizedPathAddition);
    if bDebugOutput:
      print("  => REL PATH");
      print("    CWD:     %s" % sCWD);
      print("    Path:      %s" % sNormalizedPath);
      print("    Addition:  %s" % sNormalizedPathAddition);
      print("  * Normalized:  %s" % sNormalizedPath);
    return sNormalizedPath;
  else:
    # Non-windows OS.
    if sPath.startswith(os.sep):
      sNormalizedPath = os.sep + fsNormalizePathSection(sPath[1:]);
      if bDebugOutput:
        print("  => ABS PATH");
        print("    Path:      %s" % sNormalizedPath);
        print("    Addition:  %s" % sNormalizedPathAddition);
      return fsJoinPathSections(sNormalizedPath, sNormalizedPathAddition);
    sNormalizedPath = fsNormalizePathSection(sPath);
    if bDebugOutput:
      print("  => REL PATH");
      print("    CWD:     %s" % sCWD);
      print("    Path:      %s" % sNormalizedPath);
      print("    Addition:  %s" % sNormalizedPathAddition);
    return fsJoinPathSections(sCWD, sNormalizedPath, sNormalizedPathAddition);
