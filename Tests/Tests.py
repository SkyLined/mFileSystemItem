from fTestDependencies import fTestDependencies;
fTestDependencies();

from mDebugOutput import fEnableDebugOutputForClass, fEnableDebugOutputForModule, fTerminateWithException;
try:
  # Testing is currently extremely rudimentary.
  from cFileSystemItem import cFileSystemItem;
  cFileSystemItem();
except Exception as oException:
  fTerminateWithException(oException);