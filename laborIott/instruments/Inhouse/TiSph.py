from laborIott.instruments.instrument import Instrument

requests = { 'REQ_ECHO':0,'REQ_SET_SPEED' : 1, 'REQ_GET_SPEED' : 2, 'REQ_SET_DELTA' : 3, 
'REQ_GET_DELTA' : 4, 'REQ_STOP' : 5, 'REQ_SET_RELEASE' : 6,'REQ_SET_DIGI_OUT': 7, 'REQ_GET_WAVELENGTH' : 8}


class TiSph(Instrument):
	'''
	This ver2 class refers to V-USB connected complete TiSph instrument
	(turning + wavemeter + shutter). We might need separate classes for
	wavemeter, V-USB turning (+ shutter) or COM port turning alone.

	'''


	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "TiSph", **kwargs)
		#adapter will be USBAdapter in this case
		self.shut = 0

	#I would say mostly connect-disconnect should be fine from the base
	#implement:
	#getwl
	#setwl
	#ismoving - could also signal how the moving ended - if sufficient accuracy was obtained or the repetitions were used up
	#speed
	#shutter

	@property
	def wavelength(self):
		ret = self.interact([requests['REQ_GET_WAVELENGTH'], 0, 0, 2])
		return (ret[0] + 256 * ret[1])/100.0
	
	@wavelength.setter
	def wavelength(self, value):
		pass
	#if we deem the setting as 'slow', we'd probably need a different thread
	# if we need continuous wavelength updates. However, the thread would need
	# to call wavemeter, too. But possibly it can be arranged. So there are a couple of approaches how to solve it:
	# -init motion + query. If stopped, someone would need to verify accuracy and possibly start again
	# I guess something like +- 0.01 but not more than say 5 corrections would be fine
	# Chira just commands and then user can check arrival by stepsmissing
	# In Shamrock i guess the moving is quick, so no problem to wait
	# In fact it would be good if it all happens here 

	@property
	def shutter(self):
		#we should get a GET_DIGI_OUT request, though.
		return ('closed','open')[self.shut] if self.conn is not None  else None

	@shutter.setter
	def shutter(self, val):
		try:
			#only accept these two values
			ind = ('closed','open').index(val)
		except ValueError:
			return
		ret = self.interact([requests['REQ_SET_DIGI_OUT'], ind, 0, 1])
		#think how to handle the ret value if not connected
		#well it should in general return a list, right?
		if ret is not None:
			self.shut = ind


	
