class Instrument(object):

	def __init__(self, adapter, name, **kwargs):

		self.name = name
		self.adapter = adapter
		self.connected = False #does self.connected duplicate self.adapter.conn is not None? Whatabout ZMQAdapter?
		self.connect(**kwargs)

	def __del__(self):
		if self.connected:
			self.disconnect()
		
	def connect(self, **kwargs):
		
		self.connected = self.adapter.connect(**kwargs)
		return self.connected
		
	def interact(self, command, **kwargs): #exchange?
	
		if self.connected:
			return self.adapter.interact(command, **kwargs)
		else:
			return None #or []?
			
	def disconnect(self, **kwargs):
		
		self.adapter.disconnect(**kwargs)
		self.connected = False
