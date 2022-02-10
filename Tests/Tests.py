import os, sys;
sModulePath = os.path.dirname(__file__);
sys.path = [sModulePath] + [sPath for sPath in sys.path if sPath.lower() != sModulePath.lower()];

from fTestDependencies import fTestDependencies;
fTestDependencies();

try: # mDebugOutput use is Optional
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

guExitCodeInternalError = 1; # Use standard value;
try:
  try:
    from mConsole import oConsole;
  except:
    import sys, threading;
    oConsoleLock = threading.Lock();
    class oConsole(object):
      @staticmethod
      def fOutput(*txArguments, **dxArguments):
        sOutput = "";
        for x in txArguments:
          if isinstance(x, str):
            sOutput += x;
        sPadding = dxArguments.get("sPadding");
        if sPadding:
          sOutput.ljust(120, sPadding);
        oConsoleLock.acquire();
        print(sOutput);
        sys.stdout.flush();
        oConsoleLock.release();
      @staticmethod
      def fStatus(*txArguments, **dxArguments):
        pass;
  
  bFullTests = False; # Currently not used.
  bQuickTests = False; # Currently not used.
  bEnableDebugOutput = False;
  for sArgument in sys.argv[1:]:
    if sArgument == "--debug": 
      bEnableDebugOutput = True;
    elif sArgument == "--full": 
      bFullTests = True;
    elif sArgument == "--quick": 
      bQuickTests = True;
    else:
      raise AssertionError("Unknown argument %s" % sArgument);
  
  from mFileSystemItem import cFileSystemItem;
  if bEnableDebugOutput:
    assert m0DebugOutput, \
        "The 'mDebugOutput' moduke is needed to show debug output.";
    m0DebugOutput.fEnableAllDebugOutput();
    print("*** Debug output enabled.");
  
  oTempFolder = cFileSystemItem(os.getenv("temp"));
  oTempZipFile = oTempFolder.foGetChild("cFileSystemItem test.zip");
  if oTempZipFile.fbExists():
    print("*** Deleting old %s" % oTempZipFile.sPath);
    oTempZipFile.fDelete();
  print("*** Creating %s" % oTempZipFile.sPath);
  oTempZipFile.fCreateAsZipFile();
  
  oTempTextFileInsideZipFile = oTempZipFile.foGetChild("cFileSystemItem test.text");
  print("*** Creating %s" % oTempTextFileInsideZipFile.sPath);
  oTempTextFileInsideZipFile.fWrite(b"test");
#  oTempTextFileDirectReference = cFileSystemItem(oTempTextFileInsideZipFile.sPath);
#  print("*** Reading %s" % oTempTextFileInsideZipFile.sPath);
#  assert oTempTextFileInsideZipFile.fsbRead() == b"test";

# zip files inside zip files is broken :(
#  oTempZipFileInsideZipFile = oTempZipFile.foGetChild("cFileSystemItem test child.zip");
#  print("*** Creating %s" % oTempZipFileInsideZipFile.sPath);
#  oTempZipFileInsideZipFile.fCreateAsZipFile(bParseZipFiles = True);
#  oTempTextFileInsideZipFileInsideZipFile = oTempZipFileInsideZipFile.foGetChild("cFileSystemItem test.text");
#  print("*** Creating %s" % oTempTextFileInsideZipFileInsideZipFile.sPath);
#  oTempTextFileInsideZipFileInsideZipFile.fWrite(b"test");
#  oTempTextFileDirectReference = cFileSystemItem(oTempTextFileInsideZipFileInsideZipFile.sPath);
#  print("*** Reading %s" % oTempTextFileDirectReference.sPath);
#  assert oTempTextFileDirectReference.fsbRead() == b"test";
#  print("*** Deleting %s" % oTempZipFile.sPath);
#  oTempZipFile.fDelete();
  
except Exception as oException:
  if m0DebugOutput:
    m0DebugOutput.fTerminateWithException(oException, guExitCodeInternalError, bShowStacksForAllThread = True);
  raise;
