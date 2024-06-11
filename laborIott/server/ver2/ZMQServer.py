import zmq
import pickle
from laborIott.adapter.ver2 import RNDAdapter

'''
Kuidas selle käivitamine siis hakkab käima?
import server
devdict = {"dev1":Adapter(...),
         "dev2":Adapter(...)}
inlist = (("addr1", port1),("addr2", port2))
svr = server.ZMQServer( devdict, inlist, outport)
svr.run()

'''
comm = {'connect': 0, 'interact': 1, 'disconnect': 2}


class ZMQServer(object):
	def __init__(self, devdict: dict, inlist: tuple, outport: int) -> object:
		'''
		Server base class
		Or maybe mostly not even base, you just give it the data and run it
		
		devdict = {"dev1":Adapter(...), "dev2":Adapter(...)}
			adapters should be activated beforehand
		inlist = (("addr1", port1),("addr2", port2))
			i.e. ports that should be listened for messages
		outport = number of port to use for outgoing messages
		
		Outport and inport(s) can be the same ok, but one machine can only open one outgoing port once
		(Well I think for inports, machine address + port is the unique combination)
		'''

		self.devdict = devdict
		self.timeout = 10

		# list of listened channels
		self.ch_list = []
		for inn in inlist:
			self.ch_list += [[zmq.Context().socket(zmq.SUB), zmq.Poller()]]
			sock, poll = self.ch_list[-1]
			sock.connect("tcp://%s:%d" % inn)
			sock.setsockopt(zmq.SUBSCRIBE, b'')
			poll.register(sock, zmq.POLLIN)

		# outward
		self.socket = zmq.Context().socket(zmq.PUB)
		self.socket.bind("tcp://*:%d" % outport)


	def run(self):
		#the infinite loop scanning for incoming messages
		while True:

			# cycle over the channels that we are listening
			#how can something go cross here?
			for ch in self.ch_list:
				# check if something arrived:
				if ch[1].poll(self.timeout):
					topic, record = ch[0].recv_serialized(
						deserialize=lambda msg: (msg[0].decode(), pickle.loads(msg[1])))

					#now record[0] should have the operation code
					if (dev_id in self.devdict) and (self.devdict[dev_id] is not None):
						if record[0] == comm['connect']:
							self.devdict[dev_id].connect()
						elif record[0] == comm['interact']:
							self.devdict[dev_id].interact(record[1])
						elif record[0] == comm['disconnect']:
							self.devdict[dev_id].disconnect()
					
					# some special topics? Like to stop or sth. Though who sends it?
					dev_id, op = topic.split('.')[:2]
					if (dev_id in self.devdict) and (self.devdict[dev_id] is not None):
						if op == "write":
							self.devdict[dev_id].write(record)
						elif op == "read":
							record = self.devdict[dev_id].read()
							self.socket.send_serialized(record,
														serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
						elif op == "values":
							record = self.devdict[dev_id].values(record)
							self.socket.send_serialized(record,
														serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
						elif op == "echo":
							self.socket.send_serialized(record,
														serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))

# Peaks siin mingi dummy serveri käima laskma, selleks mingi special adapter? Ja aadress localhost:5555 ilmselt.
if __name__ == '__main__':
	devdict = {"dummy": RNDAdapterAdapter()}
	inlist = (("127.0.0.0", 5555),)
	svr = ZMQServer(devdict, inlist, 5556)
	svr.run()