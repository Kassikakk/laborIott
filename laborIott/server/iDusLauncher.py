from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.SDKAdapter import SDKAdapter
import os

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

devdict = {"iDus": SDKAdapter(localPath("../instruments/Andor/Inst/atmcd32d_legacy"))}
inlist = (("172.17.202.163", 5555),)
svr = ZMQServer(devdict, inlist, 5555)
svr.run()