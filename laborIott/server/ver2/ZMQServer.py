import zmq
import pickle
from laborIott.adapters.ver2.RNDAdapter import RNDAdapter

'''
Kuidas selle käivitamine siis hakkab käima?
import server
devdict = {"dev1":Adapter(...),
         "dev2":Adapter(...)}
inlist = (("addr1", port1),("addr2", port2))
svr = server.ZMQServer( devdict, inlist, outport)
svr.run()

Oot leiutame nüüd uue asja, lihtsam server
võtame üks seade korraga
Siis vist adapter, aadress, port ja phm polegi muud vaja?
Ja sõnum on command ja sisendlist
tagasi läheb list või none? 
Hakkame otsast proovima

'''
comm = {'connect': 0, 'interact': 1, 'disconnect': 2, 'echo': 3}


class ZMQServer(object):
	def __init__(self, adapter, port = 5555) -> object:
		'''
		This server is very simple, just a layer between the actual adapter and the zmq network

		'''
		self.adapter = adapter
		# outward
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind("tcp://*:%d" % port)


	def run(self):
		#the infinite loop scanning for incoming messages
		while True:
			topic, record = self.socket.recv_serialized(
						deserialize=lambda msg: (msg[0].decode(), pickle.loads(msg[1])))
			if record[0] == comm['connect']:
				#print("callin connect")
				retval = self.adapter.connect()
			elif record[0] == comm['interact']:
				#print("callin interact")
				retval = self.adapter.interact(record[1])
			elif record[0] == comm['disconnect']:
				retval = self.adapter.disconnect()
			elif record[0] == comm['echo']:
				retval = record[1]
			self.socket.send_serialized([retval, record[2]],
			serialize=lambda rec: (topic.encode(), pickle.dumps(rec)))

					
# Peaks siin mingi dummy serveri käima laskma, selleks mingi special adapter? Ja aadress localhost:5555 ilmselt.
if __name__ == '__main__':
	svr = ZMQServer(RNDAdapter())
	svr.run()