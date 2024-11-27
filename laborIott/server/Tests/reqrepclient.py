import zmq
#import pickle
import itertools

REQUEST_TIMEOUT = 1000 #tuhat
port = "5554"
server = "tcp://172.17.203.83:%s" % port

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.REQ)
print ("Collecting updates from server...")
socket.connect(server)

for sequence in itertools.count():
    request = (0,[sequence -1 , float(sequence), "midagi"])
    
    #nüüd tuleb mingi loop
    while True:
        #socket.send_serialized(request, serialize=pickle.dumps)
        socket.send_pyobj(request)
        if (socket.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
            #reply = socket.recv_serialized(deserialize=pickle.loads)
            reply = socket.recv_pyobj()
            print(reply)
            break
        
        print("got taimaut")
        socket.setsockopt(zmq.LINGER, 0)
        socket.close()
        
        socket = context.socket(zmq.REQ)
        socket.connect(server)
