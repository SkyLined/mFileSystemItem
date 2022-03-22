
class cFileSystemItemException(Exception):
  def __init__(oSelf, sMessage, *, o0FileSystemItem = None, dxDetails = None):
    assert isinstance(dxDetails, dict), \
        "dxDetails must be a dict, not %s" % repr(dxDetails);
    oSelf.sMessage = sMessage;
    oSelf.o0FileSystemItem = o0FileSystemItem;
    oSelf.dxDetails = dxDetails;
    Exception.__init__(oSelf, sMessage, o0FileSystemItem, dxDetails);
  
  def fasDetails(oSelf):
    return (
      (["Path: %s" % oSelf.o0FileSystemItem.sPath] if oSelf.o0FileSystemItem else [])
      + ["%s: %s" % (str(sName), repr(xValue)) for (sName, xValue) in oSelf.dxDetails.items()]
    );
  def __str__(oSelf):
    return "%s (%s)" % (oSelf.sMessage, ", ".join(oSelf.fasDetails()));
  def __repr__(oSelf):
    return "<%s.%s %s>" % (oSelf.__class__.__module__, oSelf.__class__.__name__, oSelf);

acExceptions = [
  cFileSystemItemException,
];