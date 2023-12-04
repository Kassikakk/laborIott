

class Adapter(object):
	"""
	Base class for Adapter objects
	"""

	def __init__(self, **kwargs):
		pass

	def __del__(self):
		pass
		
	def connect(self, **kwargs):
		return None
		
	def interact(self, command, **kwargs): #exchange?
		return None
			
	def disconnect(self, **kwargs):
		pass