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
		try:
			
			self.conn = serial.Serial(self.port, **self.portargs)
			if self.conn.is_open:
				return True
			else:
				#print("Couldn't open connection")
				self.conn = None
				return False
			
		except Exception as e:
			#indicate an error
			print(str(e))
			self.conn = None
			return False
			
				
	def interact(self,command):
		# command should be a list of [commandstring, waitResponse (bool)]
		if self.conn is None:
			return None
		waitResponse = command[1]
		if len(command[0]) > 0:
			#write to port
			self.conn.write(command[0].encode())
		if waitResponse:
			#delay here needed?
			self.conn.flush() #this should make sure all data is written
			#note however that readlines() depends on timeout,
			lines = self.conn.readlines()
			#print(len(lines) == 0) #means timeout
			#TODO: maybe we should count consecutive timeouts and set a limit when to throw some exception
			return [""] if len(lines) == 0 else list(map(lambda x: x.decode(),lines)) 
		else:
			return None


	def disconnect(self):
		if isinstance(self.conn, serial.Serial) and self.conn.is_open:
			self.conn.close()


