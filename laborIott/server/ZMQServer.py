import zmq
import pickle
from laborIott.adapter import DummyAdapter

'''
Kuidas selle käivitamine siis hakkab käima?
import server
devdict = {"dev1":Adapter(...),
         "dev2":Adapter(...)}
inlist = (("addr1", port1),("addr2", port2))
svr = server.LabServer( devdict, inlist, outport)
svr.run()

'''


class ZMQServer(object):
	def __init__(self, devdict: dict, inlist: tuple, outport: int) -> object:
		# actual server
		# it could be beneficial to make a base class + specifics
		# but let's see
		# there should be a dict of devices, "dev_id":adapter
		# None can fytify that the device is not present

		self.devdict = devdict
		self.timeout = 0.1

		# list of listened channels
		self.ch_list = []
		for inn in inlist:
			# siin tuleb uurida, mispidi töötab
			self.ch_list += [[zmq.Context().socket(zmq.SUB), zmq.Poller()]]
			sock, poll = self.ch_list[-1]
			sock.connect("tcp://%s:%d" % inn)
			sock.setsockopt(zmq.SUBSCRIBE, b'')
			poll.register(sock, zmq.POLLIN)

		# outward
		self.socket = zmq.Context().socket(zmq.PUB)
		self.socket.bind("tcp://*:%d" % outport)

	# let's put this into some run() or something
	def run(self):
		while True:

			# cycle over some channels that we are listening
			for ch in self.ch_list:
				# check if something arrived:
				if ch[1].poll(self.timeout):
					topic, record = ch[0].recv_serialized(
						deserialize=lambda msg: (msg[0].decode(), pickle.loads(msg[1])))
					# some special topics? Like to stop or sth. Though who sends it?
					dev_id, op = topic.split('.')
					print(dev_id,op)
					if (dev_id in self.devdict) and (self.devdict[dev_id] is not None):
						if op == "write":
							print("write" + record)
							self.devdict[dev_id].write(record)
						elif op == "read":
							record = self.devdict[dev_id].read()
							self.socket.send_serialized(record,
														serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
							print("read" + record)
						elif op == "values":
							print("values_in" + record)
							record = self.devdict[dev_id].values(record)
							self.socket.send_serialized(record,
														serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
							print("values_out" + record)
						elif op == "echo":
							self.socket.send_serialized(record,
														serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))

# Peaks siin mingi dummy serveri käima laskma, selleks mingi special adapter? Ja aadress localhost:5555 ilmselt.
if __name__ == '__main__':
	devdict = {"dummy": DummyAdapter()}
	inlist = (("127.0.0.0", 5555),)
	svr = ZMQServer(devdict, inlist, 5556)
	svr.run()