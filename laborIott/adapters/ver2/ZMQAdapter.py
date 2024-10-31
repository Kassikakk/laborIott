import pickle
import zmq
from laborIott.adapters.adapter import Adapter
from threading import Event, Lock

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
	def __init__(self, address, port = 5555):
		super().__init__()

		self.server = "tcp://%s:%d" % (address, port)
		self.timeout = 200 # milliseconds for single poll
		self.repeat = 10 #reconnections before giving up
		self.context = zmq.Context()
		self.socket = None #set in the connect
		#We don't want to cross sendings from different threads possibly
		self.lock = Lock()

		

		

	def __del__(self):
		#self.disconnect()
		#Vot ma ei tea, siin tundub, et zmq kuidagi disconnectib ise juba ja siis enam ei tööta see
		pass
		
	def connect(self, **kwargs):
		"""
		The connect function is first called by the instrument's 
		__init__ function and should return a boolean value whether the 
		instrument is ready to use
		To fascilitate reconnecting, all the relevant data should generally be
		written into class variables
		"""
		#First establish the zmq connection

		accepted = False
		# establish connection, deal with "slow start" effect
		
		while not accepted:
			self.sock  = self.context.socket(zmq.REQ)
			self.sock.connect(self.server)
			accepted = (self.send_recv(comm['echo'], []) is not None)
			#log.info("Attempting connection {}".format(self.counter))
			print("echo ok" if accepted else "no echo" )
		
		ret = self.send_recv(comm['connect'], [])
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
		ret = self.send_recv(comm['interact'], command)
		if ret is None:
			return []
		return ret
			
	def disconnect(self, **kwargs):
		"""
		Should bring the connection to a state from which either shutdown or reconnection is possible
		"""

		#Send the disconnect message and get the result
		ret = self.send_recv(comm['disconnect'], [])
		#The problem is not that bad here, 		
		self.sock.close()
		return True


	def send_recv(self, command, args):

		request = [command, args]
		counter = 0
		while True:
			#print("Sending ",request,self.clear_to_send.is_set())
			with self.lock:
				self.sock.send_pyobj(request)
				if (self.sock.poll(self.timeout) & zmq.POLLIN) != 0:
					#reply = socket.recv_serialized(deserialize=pickle.loads)
					reply = self.sock.recv_pyobj()
					#print("	Recving ",request, reply)
					#print(reply)
					break

			counter += 1
			print("going for reconn ", counter)
			
			self.sock.setsockopt(zmq.LINGER, 0)
			self.sock.close()
			if counter >= self.repeat:
				reply = None
				break
			self.sock = self.context.socket(zmq.REQ)
			self.sock.connect(self.server)

		return reply