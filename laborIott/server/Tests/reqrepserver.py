import zmq
import pickle
from time import sleep
REQUEST_TIMEOUT = 100

port = "5554"
topic = "serrver"
server = "tcp://*:%s" % port


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

while True:
	#if poll...
	if (socket.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
		#request = socket.recv_serialized(deserialize=pickle.loads)
		request = socket.recv_pyobj()
		print(request)
		#nüüd peaks midagi tagasi kaa saatma
		sleep(0.2)
		reply = None #request[1]
		#socket.send_serialized(reply, serialize=pickle.dumps)
		socket.send_pyobj(reply)
