import logging
import pickle
import zmq


import numpy as np

from laborIott.adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ServerAdapter(Adapter):
	'''
	Class to communicate with a remote TCP Server
	via pickled zmq port
	implementing read, write, values
	
	'''
	def __init__(self, id, address, inport, outport = None, **kwargs):
		super().__init__()
		if outport is None:
			outport = inport
		self.id = id
		
		#outward 
		self.socket = zmq.Context().socket(zmq.PUB)
		self.socket.bind("tcp://*:%d" % outport)

	def write(self, command):
		#topic needs to contain both instrument (actual adapter) and operation data
		#i'm afraid server needs to be running first
		#there needs to be some id identifying which instrument the data is being sent to
		topic = self.id + ".write"
		self.socket.send_serialized(command,serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
