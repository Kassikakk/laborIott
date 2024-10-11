from laborIott.server.ver2.ZMQServer import ZMQServer
from laborIott.adapters.ver2.SDKAdapter import SDKAdapter
import os




svr = ZMQServer(SDKAdapter("usbdll", False), port=5554)
svr.run()
