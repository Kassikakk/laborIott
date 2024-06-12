import pickle
import zmq
from laborIott.adapters.adapter import Adapter

comm = {'connect': 0, 'interact': 1, 'disconnect': 2, 'echo': 3}

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

		self.id = id
		self.address = address
		self.inport = inport
		self.outport = inport if outport is None else outport
		
		self.insock = None
		self.poller = None
		self.outsock = None
		
		self.timeout = 200 # milliseconds for single poll
		self.globtimeout = 5000 #global timeout to wait for response
		self.repeat = int(self.globtimeout / self.timeout) 
		#count the messages and add this as an ID to match the return
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
		self.insock = zmq.Context().socket(zmq.SUB)
		self.poller = zmq.Poller()
		self.insock.connect("tcp://%s:%d" % (self.address, self.inport))
		self.insock.setsockopt(zmq.SUBSCRIBE, b'')
		self.poller.register(self.insock, zmq.POLLIN)
		
		
		
		
		#outward 
		self.outsock = zmq.Context().socket(zmq.PUB)
		self.outsock.bind("tcp://*:%d" % self.outport)
		topic = self.id + ".connect"
		#log.debug(topic + " : " + command)

		# establish connection, deal with "slow start" effect
		self.repeat = 2 #low number to speed up starting
		while self.send_recv(self.id,[comm['echo'], []]) is None:
			#log.info("Attempting connection {}".format(self.counter))
			pass
			#we could cut here according to self.counter value if no one comes online

		#set a longer global timeout
		self.repeat = int(self.globtimeout / self.timeout) #global timeout / single shot timeout



		ret = self.send_recv(self.id,[comm['connect'], []])
		#The problem is that if that returns None, this basically means timeout or crossed messages
		# so you still don't know if the device connected or not
		if ret is None:
			return False
		
		return ret
		
	def interact(self, command, **kwargs): #exchange?
		"""
		performs (generally) a two-way interaction and should return a list of results
		interpreting the list is up to the instrument
		"""
		ret = self.send_recv(self.id,[comm['disconnect'], command])
		if ret is None:
			return []
		return ret
			
	def disconnect(self, **kwargs):
		"""
		Should bring the connection to a state from which either shutdown or reconnection is possible
		"""

		#Send the disconnect message and get the result
		ret = self.send_recv(self.id,[comm['disconnect'], []])
		#The problem is not that bad here, 
		
		self.poller.unregister(self.insock)
		self.insock.close()
		self.outsock.close()
		return True

	def send_recv(self, topic, record):
		#add the counter
		self.counter += 1
		record += [self.counter]
		self.outsock.send_serialized(record, serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
		# wait for reply here
		for i in range(self.repeat):
			if self.poller.poll(self.timeout):
				topic1, record = self.insock.recv_serialized(
						deserialize=lambda msg: (msg[0].decode(), pickle.loads(msg[1])))
				#now record is the returned list, with [0] as the function return and [1] as the counter
				if (topic1 == topic) and (record[1] == self.counter):
					#log.debug(record)
					return record[0]
				else:
					#log.info("Mistopicd: " + topic1 + " in rsp to " + topic)
					pass
		#log.info("Timeout: " + topic)
		return None