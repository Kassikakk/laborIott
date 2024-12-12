from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.RNDAdapter import RNDAdapter
import os



devdict = {"Mock": RNDAdapter()}
inlist = (("localhost", 5556),)
svr = ZMQServer(devdict, inlist, 5555)
svr.run()
