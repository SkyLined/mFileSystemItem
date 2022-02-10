import os;

if os.name == 'nt':
  from mWindowsSDK.mKernel32 import oKernel32DLL;
  from mWindowsSDK import *;

from .fsGetWindowsPath import fsGetWindowsPath;

def fs0GetDOSPath(sPath):
  if os.name != 'nt':
    return sPath; # Not on Windows: same as original.
  sWindowsPath = fsGetWindowsPath(sPath);
  if not os.path.exists(sWindowsPath):
    return None;
  opsWindowsPath = LPCWSTR(foCreateBuffer(sWindowsPath), bCast = True);
  odwRequiredBufferSizeInChars = oKernel32DLL.GetShortPathNameW(
    opsWindowsPath,
    NULL,
    0
  );
  assert odwRequiredBufferSizeInChars.value != 0, \
        "GetShortPathNameW('...', NULL, 0) => Error 0x%08X" % oKernel32DLL.GetLastError();
  oBuffer = foCreateBuffer(odwRequiredBufferSizeInChars.value);
  dwUsedBufferSizeInChars = oKernel32DLL.GetShortPathNameW(
    opsWindowsPath,
    PWSTR(oBuffer, bCast = True),
    odwRequiredBufferSizeInChars
  );
  assert dwUsedBufferSizeInChars.value != 0, \
      "GetShortPathNameW('...', 0x%08X, 0x%X) => Error 0x%08X" % \
      (pBuffer, odwRequiredBufferSizeInChars.value, oKernel32DLL.GetLastError());
  sDOSPath = fsGetBufferString(oBuffer);
  if sDOSPath.startswith("\\\\?\\"):
    sDOSPath = sDOSPath[len("\\\\?\\"):];
    if sDOSPath.startswith("UNC\\"):
      sDOSPath = "\\" + sDOSPath[len("UNC"):];
  return sDOSPath;
