import pickle
import zmq
from laborIott.adapters.adapter import Adapter


class ZMQAdapter(Adapter):
	'''
	Class to communicate with a remote TCP Server
	via pickled zmq port
	topic needs to contain both instrument (actual adapter) and operation data
	i'm afraid server needs to be running first
	there needs to be some id identifying which instrument the data is being sent to

	Isegi võiks küsida, et kas ei peaks portide connectimise ühendama üldise connect-disconnect süsteemiga?
	Selle mõttega, et äkki ka sellele oleks vaja teha reconnectimist?
	Võib-olla on see vajalik mõte. 
	
	'''
	def __init__(self, id, address, inport, outport = None, **kwargs):
		super().__init__()
		if outport is None:
			outport = inport
		self.id = id
		self.insock = None
		self.poller = None
		self.outsock = None
		self.timeout = 200 # milliseconds for single poll
		self.globtimeout = 5000 #global timeout to wait for response
		self.counter = 0


		

	def __del__(self):
		self.disconnect()
		
	def connect(self, **kwargs):
		"""
		The connect function is first called by the instrument's 
		__init__ function and should return a boolean value whether the 
		instrument is ready to use
		To fascilitate reconnecting, all the relevant data should generally be
		written into class variables
		"""
		#First establish the zmq connection
		# inward
		self.insock, self.poller = zmq.Context().socket(zmq.SUB), zmq.Poller()
		self.insock.connect("tcp://%s:%d" % (address, inport))
		self.insock.setsockopt(zmq.SUBSCRIBE, b'')
		self.poller.register(self.insock, zmq.POLLIN)
		
		
		#count the messages and add this as an ID to match the return
		self.counter = 0
		
		#outward 
		self.outsock = zmq.Context().socket(zmq.PUB)
		self.outsock.bind("tcp://*:%d" % outport)
		topic = self.id + ".connect"
		#log.debug(topic + " : " + command)
		self.outsock.send_serialized(command, serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
		return True
		
	def interact(self, command, **kwargs): #exchange?
		"""
		performs (generally) a two-way interaction and should return a list of results
		interpreting the list is up to the instrument
		"""
		return None
			
	def disconnect(self, **kwargs):
		"""
		Should bring the connection to a state from which either shutdown or reconnection is possible
		"""
		#Send the disconnect message and get the result
		self.poller.unregister(self.insock)
		self.insock.close()
		self.outsock.close()
