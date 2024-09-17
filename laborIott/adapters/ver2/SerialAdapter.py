import serial
from laborIott.adapters.adapter import Adapter


class SerialAdapter(Adapter):
	""" Adapter class for using the Python Serial package to allow
	serial communication to instruments
	"""

	def __init__(self, port, **kwargs):
		super().__init__()
		self.port = port
		#kwargs may contain arguments for opening the connection
		#defaults are: baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False
		self.portargs = kwargs #we should make sure that timeout is included

	def connect(self):
		#avoid reopening
		if isinstance(self.conn, serial.Serial) and self.conn.is_open:
			return True
		#try:
			
			self.conn = serial.Serial(self.port, **self.portargs)
			if self.conn.is_open:
				return True
			else:
				#print("Couldn't open connection")
				self.conn = None
				return False
			'''
		except Exception as e:
			#indicate an error
			print(str(e))
			self.conn = None
			return False
			'''
				
	def interact(self,command, waitResponse = True, **kwargs):
		if self.conn is None:
			return []
		if len(command) > 0:
			#write to port
			self.conn.write(command.encode())
		if waitResponse:
			#delay here needed?
			self.conn.flush() #this should make sure all data is written
			#note however that readlines() depends on timeout,
			return list(map(lambda x: x.decode(),self.connection.readlines()))
		else:
			return []


	def disconnect(self):
		if isinstance(self.conn, serial.Serial) and self.conn.is_open:
			self.conn.close()


