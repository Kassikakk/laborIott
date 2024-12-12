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
		
	def interact(self, command, dummy = None): #exchange?
		'''
		command: a simple command or a list of many parameters, ready for the adapter to process
		dummy: something to return if anything is wrong, to keep the instrument running, if needed

		'''
	
		if self.connected:
			try:
				#print(command)
				ret = self.adapter.interact(command)
				return ret if ret is not None else dummy
				#we may have to use some method to check if the adapter's response is a normal one
				#ok let's try like this. May the adapter return None if anything is out of order
				#Then here we return dummy.
				
			except Exception as e:
				#there is a problem with the device, disconnect
				#if there are some specific problems, solve them in the adapter
				#TODO: log error message here
				print(command)
				print(f"An interact error: {e}")
				self.disconnect()
				return dummy
		else:
			return dummy
			
	def disconnect(self, **kwargs):
		
		self.connected = False
		try:
			self.adapter.disconnect(**kwargs)
		except:
			#TODO: log message here
			pass
			
		
