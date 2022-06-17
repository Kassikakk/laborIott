import pickle
import zmq
from laborIott.adapter import Adapter
import logging

#set up logging if needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
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
		self.timeout = 100 # milliseconds
		self.repeat = int(1000 / self.timeout) #global timeout / single shot timeout
		
		#outward 
		self.outsock = zmq.Context().socket(zmq.PUB)
		self.outsock.bind("tcp://*:%d" % outport)
		# establish connection
		for i in range(5):
			if self.exchange("",".echo") is not None:
				break
			if i==4:
				print("Server is not responding")

	def write(self, command):
		topic = self.id + ".write"
		self.outsock.send_serialized(command, serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))

	def exchange(self, command, comm_id):
		# common routine for two-way communication
		topic = self.id + comm_id
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
		log.debug("No result")
		return None

	def read(self):
		return self.exchange("",".read")

	def values(self,command):
		return self.exchange(command, ".values")
