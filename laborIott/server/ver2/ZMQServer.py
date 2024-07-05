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
		self.sock = self.context.socket(zmq.REP)
		self.sock.bind("tcp://*:%d" % port)


	def run(self):
		#the infinite loop scanning for incoming messages
		while True:

			request = self.sock.recv_pyobj()
			if request[0] == comm['connect']:
				#print("callin connect")
				reply = self.adapter.connect()
			elif request[0] == comm['interact']:
				#print("callin interact")
				reply = self.adapter.interact(request[1])
			elif request[0] == comm['disconnect']:
				reply = self.adapter.disconnect()
			elif request[0] == comm['echo']:
				reply = request[1]

			self.sock.send_pyobj(reply)

			

					
# Peaks siin mingi dummy serveri käima laskma, selleks mingi special adapter? Ja aadress localhost:5555 ilmselt.
if __name__ == '__main__':
	svr = ZMQServer(RNDAdapter())
	svr.run()