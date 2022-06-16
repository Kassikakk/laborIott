from laborIott.server.ZMQServer import ZMQServer
import os

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

devdict = {"iDus": SDKAdapter(localPath("../Inst/atmcd32d_legacy"))}
inlist = (("mikro-spektro", 5555),)
svr = ZMQServer(devdict, inlist, 5555)
svr.run()