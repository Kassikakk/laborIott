import pickle
import zmq



address = "jobinyvon"
inport = 5555
outport = 5555


insock, poller = zmq.Context().socket(zmq.SUB), zmq.Poller()
insock.connect("tcp://%s:%d" % (address, inport))
insock.setsockopt(zmq.SUBSCRIBE, b'')
poller.register(insock, zmq.POLLIN)
timeout = 100  # milliseconds
repeat = int(1000 / timeout)  # global timeout / single shot timeout

outsock = zmq.Context().socket(zmq.PUB)
outsock.bind("tcp://*:%d" % outport)
topic = "iDus.echo"
for i in range(5):
	command = "calling {}".format(i)
	outsock.send_serialized(command, serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))
	for j in range(repeat):
			if poller.poll(timeout):
				topic1, record = insock.recv_serialized(
						deserialize=lambda msg: (msg[0].decode(), pickle.loads(msg[1])))
				if (topic1 == topic):
					print(record)
				else:
					print("midagi muud")
					break
	print("end of cycle {}". format(i))
