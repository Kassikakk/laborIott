



class Adapter(object):
	""" Base class for Adapter child classes, which adapt between the Instrument 
	object and the connection, to allow flexible use of different connection 
	techniques.

	This class should only be inherited from.

	:param preprocess_reply: optional callable used to preprocess strings
		received from the instrument. The callable returns the processed string.
	:param kwargs: all other keyword arguments are ignored.
	"""
	def __init__(self, **kwargs):
		self.connection = None

	def __del__(self):
		"""Close connection upon garbage collection of the device"""
		if self.connection is not None:
			self.connection.close()

	def write(self, command):
		""" Writes a command to the instrument

		:param command: command string to be sent to the instrument
		"""
		raise NameError("Adapter (sub)class has not implemented writing")

	def ask(self, command):
		""" Writes the command to the instrument and returns the resulting 
		ASCII response

		:param command: command string to be sent to the instrument
		:returns: String ASCII response of the instrument
		"""
		self.write(command)
		return self.read()

	def read(self):
		""" Reads until the buffer is empty and returns the resulting
		ASCII respone

		:returns: String ASCII response of the instrument.
		"""
		raise NameError("Adapter (sub)class has not implemented reading")
	'''

	def values(self, command, separator=',', cast=float, preprocess_reply=None):
		""" Writes a command to the instrument and returns a list of formatted
		values from the result 

		:param command: SCPI command to be sent to the instrument
		:param separator: A separator character to split the string into a list
		:param cast: A type to cast the result
		:param preprocess_reply: optional callable used to preprocess values
			received from the instrument. The callable returns the processed string.
			If not specified, the Adapter default is used if available, otherwise no
			preprocessing is done.
		:returns: A list of the desired type, or strings where the casting fails
		"""
		results = str(self.ask(command)).strip()
		if callable(preprocess_reply):
			results = preprocess_reply(results)
		elif callable(self.preprocess_reply):
			results = self.preprocess_reply(results)
		results = results.split(separator)
		for i, result in enumerate(results):
			try:
				if cast == bool:
					# Need to cast to float first since results are usually
					# strings and bool of a non-empty string is always True
					results[i] = bool(float(result))
				else:
					results[i] = cast(result)
			except Exception:
				pass  # Keep as string
		return results

	def binary_values(self, command, header_bytes=0, dtype=np.float32):
		""" Returns a numpy array from a query for binary data 

		:param command: SCPI command to be sent to the instrument
		:param header_bytes: Integer number of bytes to ignore in header
		:param dtype: The NumPy data type to format the values with
		:returns: NumPy array of values
		"""
		raise NameError("Adapter (sub)class has not implemented the "
						"binary_values method")
'''

class DummyAdapter(object):
	def __init__(self, **kwargs):
		super().__init__()
		self.written = "None"

	def write(self, command):
		self.written = command

	def read(self):
		return self.written

	def values(self, command):
		return command