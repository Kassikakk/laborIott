from laborIott.server.ver2.ZMQServer import ZMQServer
from laborIott.adapters.ver2.RNDAdapter import RNDAdapter
import os



devdict = {"Mock": RNDAdapter()}
inlist = (("localhost", 5556),)
svr = ZMQServer(devdict, inlist, 5555)
svr.run()