from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.USBAdapter import USBAdapter
import os


svr = ZMQServer(USBAdapter(0xcacc, 0x0002))
svr.run()
