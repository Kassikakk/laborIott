from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.SDKAdapter import SDKAdapter
import os




svr = ZMQServer(SDKAdapter("usbdll", False), port=5554)
svr.run()
