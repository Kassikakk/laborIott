from laborIott.server.ZMQServer import ZMQServer
from laborIott.adapters.SerialAdapter import SerialAdapter
import os




svr = ZMQServer(SerialAdapter("/dev/ttyUSB0",baudrate=115200, timeout = 0.1), port=5554)
svr.run()
