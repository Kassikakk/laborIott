from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.serial import SerialAdapter
import os

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

devdict = {"nwp842": SerialAdapter("COM5",baudrate=115200, timeout = 0.3)}
inlist = (("mikro-spektro", 5555),)
svr = ZMQServer(devdict, inlist, 5555)
svr.run()