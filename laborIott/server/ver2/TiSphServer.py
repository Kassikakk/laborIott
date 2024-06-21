from laborIott.server.ver2.ZMQServer import ZMQServer
from laborIott.adapters.ver2.USBAdapter import USBAdapter
import os



devdict = {"TiSph": USBAdapter(0xcacc, 0x0002)}
inlist = (("localhost", 5556),)
svr = ZMQServer(devdict, inlist, 5555)
svr.run()