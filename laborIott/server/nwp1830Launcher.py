from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.SDKAdapter import SDKAdapter
import os

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

devdict = {"nwp1830": SDKAdapter(localPath("../Inst/usbdll"), False)}
inlist = (("ltfy-d116", 5555),)
svr = ZMQServer(devdict, inlist, 5555)
svr.run()