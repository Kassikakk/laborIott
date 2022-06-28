import pickle
import zmq
from laborIott.adapter import Adapter
import logging

#set up logging if needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
log.addHandler(ch)



class ZMQAdapter(Adapter):
	'''
	Class to communicate with a remote TCP Server
	via pickled zmq port
	implementing read, write, values
	topic needs to contain both instrument (actual adapter) and operation data
	i'm afraid server needs to be running first
	there needs to be some id identifying which instrument the data is being sent to
	
	'''
	def __init__(self, id, address, inport, outport = None, **kwargs):
		super().__init__()
		if outport is None:
			outport = inport
		self.id = id

		# inward
		self.insock, self.poller = zmq.Context().socket(zmq.SUB), zmq.Poller()
		self.insock.connect("tcp://%s:%d" % (address, inport))
		self.insock.setsockopt(zmq.SUBSCRIBE, b'')
		self.poller.register(self.insock, zmq.POLLIN)
		self.timeout = 200 # milliseconds for single poll
		self.globtimeout = 5000 #global timeout to wait for response
		
		#count the messages and add this as an ID to match the return
		self.counter = 0
		
		#outward 
		self.outsock = zmq.Context().socket(zmq.PUB)
		self.outsock.bind("tcp://*:%d" % outport)

		# establish connection, deal with "slow start" effect
		self.repeat = 2 #low number to speed up starting
		while self.exchange("",".echo") is None:
			log.info("Attempting connection {}".format(self.counter))
			#we could cut here according to self.counter value if no one comes online

		#set a longer global timeout
		self.repeat = int(self.globtimeout / self.timeout) #global timeout / single shot timeout


	def write(self, command):
		topic = self.id + ".write"
		log.debug(topic + " : " + command)
		self.outsock.send_serialized(command, serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))

	def exchange(self, command, comm_id):
		# common routine for two-way communication
		topic = self.id + comm_id + ".{}".format(self.counter)
		self.counter += 1
		log.debug(topic + " : " + command)
		self.outsock.send_serialized(command, serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
		# wait for reply here
		for i in range(self.repeat):
			if self.poller.poll(self.timeout):
				topic1, record = self.insock.recv_serialized(
						deserialize=lambda msg: (msg[0].decode(), pickle.loads(msg[1])))
				if (topic1 == topic):
					log.debug(record)
					return record
				else:
					log.info("Mistopicd: " + topic1 + " in rsp to " + topic)
		log.info("Timeout: " + topic)
		return None

	def read(self):
		return self.exchange("",".read")

	def values(self,command):
		return self.exchange(command, ".values")
