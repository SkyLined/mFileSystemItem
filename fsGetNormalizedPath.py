import os, threading;

def fsGetNormalizedPath(sPath, sBasePath = None):
  def fsNormalizePathInternal(sBase, sPath, bAbsolute = False):
    assert sBase is None or sBase.endswith(os.sep) or sBase.endswith(":"), \
        "Base (%s) must end with separator" % repr(sBase);
    sNormalizedPath = os.path.normpath(sPath).rstrip(os.sep);
    assert not sNormalizedPath.startswith(os.sep) and not (len(sNormalizedPath) >= 2 and sNormalizedPath[1] == ":"), \
        "Cannot normalize %s" % repr(sPath);
    if sNormalizedPath == ".":
      assert sBase, \
          "Cannot normalize absolute path %s" % repr(sPath);
      sNormalizedPath = "";
    return sBase + sNormalizedPath;
  if not sPath:
    sPath = os.getcwd();
  sOriginalPath = sPath;
  if not isinstance(sPath, str):
    sPath = str(sPath, "cp437");
  if sPath.startswith("\\\\.\\"): # Physical drive
    raise NotImplementedError();
  elif sPath.startswith("\\\\?\\"): # Extended path
    sPath = sPath[4:];
    if sPath.startswith("UNC\\"):
      # "\\?\" + "UNC\" + "<server>" + "\" + "<path>" => "\\" + "<server>" + "\" + normalize("<path>")
      sServer, sPath = sPath[4:].split("\\", 1);
      sPath = fsNormalizePathInternal("\\\\" + sServer + "\\", sPath);
    elif len(sPath) >= 3 and sPath[1:3] == ":\\":
      # "\\?\" + "X:\" + "<path>" => "X:\" + normalize("<path>")
      sPath = fsNormalizePathInternal(sPath[:3], sPath[3:]);
    elif len(sPath) >= 2 and sPath[1] == ":":
      # "\\?\" + "X:" + "<path>" => normalize("X:" + "\" + ("<CWD for X:>" + "\") + "<path>")
      sCWDPath = os.path.abspath(sPath[:2])[3:];
      if sCWDPath:
        sCWDPath += "\\";
      sPath = fsNormalizePathInternal(sPath[:2] + "\\", sCWDPath + sPath[2:]);
    else:
      # "\\?\" + "<server>" + "\" + "<path>" => "\\" + "<server>" "\" + normalize("<path>")
      sServer, sPath = sPath[4:].split("\\", 1);
      sPath = fsNormalizePathInternal("\\\\" + sServer + "\\", sPath);
  elif sPath.startswith("\\\\"):
    # "\\" "<server>" + "\" + "<path>" => "\\" + "<server>" + "\" + normalize("<path>")
    sServer, sPath = sPath[2:].split("\\", 1);
    sPath = fsNormalizePathInternal("\\\\" + sServer + "\\", sPath);
  elif len(sPath) >= 3 and sPath[1:3] == ":\\":
    # "X:\" "<path>" => "X:\" normalize("<path>")
    sPath = fsNormalizePathInternal(sPath[:3], sPath[3:]);
  elif len(sPath) >= 2 and sPath[1] == ":":
    # "X:" "<path>" => normalize("<CWD for X:>" + "\" + "<path>")
    sCWDPath = os.path.abspath(sPath[:2])[3:];
    if sCWDPath:
      sCWDPath += "\\";
    sPath = fsNormalizePathInternal(sPath[:2] + "\\", sCWDPath + sPath[2:]);
  elif sPath.startswith(os.sep) and os.name != "nt":
    # Absolute LINUX path
    sPath = fsNormalizePathInternal(None, sPath);
  else: # relative path in sBasePath or CWD.
    # "<path>" => recursive((sBasePath or "<CWD>") + "\" + "<path>")
    # Recursive
    sPath = fsGetNormalizedPath((sBasePath or os.getcwd()) + os.sep + sPath);
  # Convert to ASCII if possible
  try:
    sPath = str(sPath, encoding = "ascii");
  except:
    pass;
  return sPath;
