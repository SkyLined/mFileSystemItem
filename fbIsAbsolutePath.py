import os;

def fbIsAbsolutePath(sPath):
  if sPath.startswith(os.sep):
    return True;
  if os.name == "nt":
    if sPath.startswith(os.altsep):
      return True;
    if len(sPath) >= 2 and sPath[1] == ":":
      return True; # relative to a drive is also consider absolute.
  return False;
