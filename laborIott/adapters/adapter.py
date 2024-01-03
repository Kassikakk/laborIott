

class Adapter(object):
	"""
	Base class for Adapter objects
	"""

	def __init__(self, **kwargs):
		self.conn = None
		pass

	def __del__(self):
		self.disconnect()
		
	def connect(self, **kwargs):
		"""
		The connect function is first called by the instrument's 
		__init__ function and should return a boolean value whether the 
		instrument is ready to use
		To fascilitate reconnecting, all the relevant data should generally be
		written into class variables
		"""
		return True
		
	def interact(self, command, **kwargs): #exchange?
		"""
		performs (generally) a two-way interaction and should return a list of results
		interpreting the list is up to the instrument
		"""
		return None
			
	def disconnect(self, **kwargs):
		"""
		Should bring the connection to a state from which either shutdown or reconnection is possible
		"""
		pass