from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.SDKAdapter import SDKAdapter
import os

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

devdict = {"nwp1830": SDKAdapter(localPath("../instruments/Newport1830/Inst/usbdll"), False)}
inlist = (("ltfy-d116", 5554),)
svr = ZMQServer(devdict, inlist, 5554)
svr.run()