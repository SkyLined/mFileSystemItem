import os, sys;
sModulePath = os.path.dirname(__file__);
sys.path = [sModulePath] + [sPath for sPath in sys.path if sPath.lower() != sModulePath.lower()];

from fTestDependencies import fTestDependencies;
fTestDependencies("--automatically-fix-dependencies" in sys.argv);
sys.argv = [s for s in sys.argv if s != "--automatically-fix-dependencies"];

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
  from mFileSystemItem.fsGetNormalizedPath import fsGetNormalizedPath;
  if bEnableDebugOutput:
    assert m0DebugOutput, \
        "The 'mDebugOutput' moduke is needed to show debug output.";
    m0DebugOutput.fEnableAllDebugOutput();
    print("*** Debug output enabled.");

  sCWD = os.getcwd();
  if os.name == "nt":
    sCurrentDrive = sCWD[:2];
    for sPath, sNormalizedPath in {
      "C:\\..": None,
      "C:\\Path1\\..\\..": None,
      "CX:\\..": None,
      sCurrentDrive: sCWD,
      ("%sX\\.." % sCurrentDrive): sCWD,
      ("%s.\\Path1" % sCurrentDrive): sCWD + "\\Path1",
      "C:\\Path1": "C:\\Path1",
      "C:\\Path1\\": "C:\\Path1",
      "C:\\Path1\\Path2": "C:\\Path1\\Path2",
      "C:\\\\Path1\\": "C:\\Path1",
      "C:\\\\Path1\\\\Path2": "C:\\Path1\\Path2",
      "C:\\Path1\\.\\Path2": "C:\\Path1\Path2",
      "C:\\Path1\\..\\Path2": "C:\\Path2",
      "\\\\?\\C:\Path1": "C:\\Path1",
      "\\\\Server\\Share": "\\\\Server\\Share",
      "\\\\Server\\Share\\Path1": "\\\\Server\\Share\\Path1",
      "\\\\Server\\Share\\Path1\\Path2": "\\\\Server\\Share\\Path1\\Path2",
      "\\\\?\\Server\\Share\\Path1\\Path2": "\\\\Server\\Share\\Path1\\Path2",
      "\\\\?\\UNC\\Server\\Share\\Path1\\Path2": "\\\\Server\\Share\\Path1\\Path2",
    }.items():
      if sNormalizedPath:
        assert fsGetNormalizedPath(sPath) == sNormalizedPath, \
            "fsGetNormalizedPath(%s) == %s (expect %s)" % (
              repr(sPath),
              repr(fsGetNormalizedPath(sPath)),
              repr(sNormalizedPath)
            );
        print("+ fsGetNormalizedPath(%s) => %s" % (repr(sPath), repr(sNormalizedPath)));
      else:
        try:
          fsGetNormalizedPath(sPath);
        except ValueError as oException:
          print("+ fsGetNormalizedPath(%s) => %s" % (repr(sPath), repr(oException)));
        else:
          assert False, \
            "fsGetNormalizedPath(%s) == %s (expected ValueError)" % (
              repr(sPath),
              repr(fsGetNormalizedPath(sPath)),
            );



  oTempFolder = cFileSystemItem(os.getenv("temp"));
  oTempZipFile = oTempFolder.foGetChild("cFileSystemItem test.zip");
  if oTempZipFile.fbExists():
    print("*** Deleting old %s" % oTempZipFile.sPath);
    oTempZipFile.fDelete();
# Zip file support is broken
#  print("*** Creating %s" % oTempZipFile.sPath);
#  oTempZipFile.fCreateAsZipFile();
#  
#  oTempTextFileInsideZipFile = oTempZipFile.foGetChild("cFileSystemItem test.text");
#  print("*** Creating %s" % oTempTextFileInsideZipFile.sPath);
#  oTempTextFileInsideZipFile.fWrite(b"test");
#  print("*** Reading %s" % oTempTextFileInsideZipFile.sPath);
#  sbTempTextFileContent = oTempTextFileInsideZipFile.fsbRead();
#  assert sbTempTextFileContent == b"text", \
#      "Cannot read newly created text file inside zip file: %s" % repr(sbTempTextFileContent);
#  oTempTextFileAbsoluteReference = cFileSystemItem(oTempTextFileInsideZipFile.sPath);
#  sbTempTextFileContent  = oTempTextFileAbsoluteReference.fsbRead();
#  assert sbTempTextFileContent == b"text", \
#      "Cannot read text file inside zip file through absolute reference: %s" % repr(sbTempTextFileContent);

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
