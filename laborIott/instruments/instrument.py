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
		try:
			self.connected = self.adapter.connect(**kwargs)
		except:
			#TODO: log error message here
			#do we have to return from here?
			pass
		return self.connected
		
	def interact(self, command, **kwargs): #exchange?
	
		if self.connected:
			try:
				return self.adapter.interact(command, **kwargs)
			except:
				#there is a problem with the device, disconnect
				#if there are some specific problems, solve them in the adapter
				#TODO: log error message here
				self.disconnect()
				return None
		else:
			return None #or []?
			
	def disconnect(self, **kwargs):
		
		self.connected = False
		try:
			self.adapter.disconnect(**kwargs)
		except:
			#TODO: log message here
			pass
			
		
