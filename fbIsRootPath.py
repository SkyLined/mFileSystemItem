import os, re;

from .fsGetNormalizedPath import fsGetNormalizedPath;

rRootUNCPath = re.compile(
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
  r"([\\\/])*"            # * optional { "\" or "/" any number of times }
  r"\Z"
);
rRootDriveLetter = re.compile(
  r"\A"
  r"([A-Za-z]:)"          # * { drive letter ":" }
  r"([\\\/])*"            # * optional { "\" or "/" any number of times }
  r"\Z"
);

def fbIsRootPath(sPath):
  if os.name == "nt":
    if rRootUNCPath.match(sPath) or rRootDriveLetter.match(sPath):
      return True;
  elif sPath[:1] == os.sep:
    return True;
  return False;
