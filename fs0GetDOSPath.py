from .fsGetWindowsPath import fsGetWindowsPath;

from mWindowsSDK import *;

def fs0GetDOSPath(sPath):
  sWindowsPath = fsGetWindowsPath(sPath);
  if not os.path.exists(sWindowsPath):
    return None;
  from mWindowsSDK.mKernel32 import oKernel32DLL;
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
