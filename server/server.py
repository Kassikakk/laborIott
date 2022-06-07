def __init__(self, outport):
#actual server
#it could be beneficial to make a base class + specifics
#but let's see
#there should be a dict of devices, "dev_id":adapter
#None can fytify that the device is not present
ad1 = None
ad2 = None
devdict = {"dev1":ad1, "dev2":ad2}
#list of listened channels
ch_list = (socket(addr1, port1),socket(addr2, port2))
		#outward 
		self.socket = zmq.Context().socket(zmq.PUB)
		self.socket.bind("tcp://*:%d" % outport)



#let's put this into some run() or something
def run(self):
while True:
	
	#cycle over some channels that we are listening
	for ch in ch_list:
		#check if something arrived:
		if ch.something_arrived:
			topic, record = ch.unpickle()
			#some special topics? Like to stop or sth. Though who sends it?
			dev_id,op = topic.split('.')
			if (dev_id in devdict) and (devdict[dev_id] is not None):
				if (op == "write"):
					devdict[dev_id].write(record)
				elif (op == "read"):
					self.socket.send_serialized(devdict[dev_id].read())
				elif (op == "values"):
					self.socket.send_serialized(devdict[dev_id].values(record))
	
