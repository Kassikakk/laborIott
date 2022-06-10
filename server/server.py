'''
Kuidas selle käivitamine siis hakkab käima?
import server
devdict = {"dev1":Adapter(...),
         "dev2":Adapter(...)}
inlist = (("addr1", port1),("addr2", port2))
svr = server.LabServer( devdict, inlist, outport)
svr.run()

'''


class LabServer(object):
	def __init__(self, devdict, inlist, outport):
		# actual server
		# it could be beneficial to make a base class + specifics
		# but let's see
		# there should be a dict of devices, "dev_id":adapter
		# None can fytify that the device is not present

		self.devdict = devdict

		# list of listened channels
		self.ch_list = []
		for inn in inlist:
			# siin tuleb uurida, mispidi töötab
			self.ch_list += [[zmq.Context().socket(zmq.SUB), zmq.Poller()]]
			sock,poll = self.ch_list[-1]
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
				if ch[1].poll(0.1):
					topic, record = ch[0].recv_serialized(unpickle()
					# some special topics? Like to stop or sth. Though who sends it?
					dev_id, op = topic.split('.')
					if (dev_id in self.devdict) and (self.devdict[dev_id] is not None):
						if op == "write":
							self.devdict[dev_id].write(record)
						elif op == "read":
							self.socket.send_serialized(self.devdict[dev_id].read())
						elif op == "values":
							self.socket.send_serialized(self.devdict[dev_id].values(record))
