import os;

def fsGetWindowsPath(sPath):
  if os.name != 'nt':
    return sPath; # Not on Windows: same as original.
  if not sPath.startswith(r"\\"):
    sDrive, sPath = os.path.splitdrive(sPath);
    if not sDrive:
      # No drive provided: use global CWD
      sDrive, sCWDPath = os.path.splitdrive(os.getcwd());
    else:
      # Drive provided: use CWD for the specified drive
      sCWDPath = os.path.abspath(sDrive)[2:];
    if sPath[0] != "\\":
      # Path is relative to CWD path
      sPath = os.path.join(sCWDPath, sPath);
    return "\\\\?\\" + sDrive + os.path.normpath(sPath);
  return "\\\\?\\UNC\\" + os.path.normpath(sPath[2:]);
