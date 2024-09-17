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
		except Exception as e:
    		# Print the error message
			print(f"An error occurred: {e}")
			#TODO: log error message here
			
		return self.connected
		
	def interact(self, command, **kwargs): #exchange?
	
		if self.connected:
			try:
				return self.adapter.interact(command, **kwargs)
			except Exception as e:
				#there is a problem with the device, disconnect
				#if there are some specific problems, solve them in the adapter
				#TODO: log error message here
				print(f"An interact error: {e}")
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
			
		
