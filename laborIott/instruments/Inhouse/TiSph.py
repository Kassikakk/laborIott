from laborIott.instruments.instrument import Instrument
from threading import Thread,Event
from time import sleep

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
		self.prec = 0.05
		self.nmperstep = 0.0205 #0.039
		self.noReps = 10
		self.moving = Event()
		self.linefree = Event()
		self.linefree.set()


	#I would say mostly connect-disconnect should be fine from the base
	#implement:
	#getwl
	#setwl
	#status- could also signal how the moving ended - if sufficient accuracy was obtained or the repetitions were used up
	#and when assigned - can force stop
	#speed
	#shutter

	def interwrap(self, command):
		#try a wrapper to thread sync here
		self.linefree.wait()
		self.linefree.clear()
		print("entering", command)
		ret = self.interact(command)
		print("->exiting", command)

		self.linefree.set()
		return ret

	def move(self, value):
		#thread function for moving
		for i in range(self.noReps):
			#find number of steps
			wl = self.wavelength
			diff = wl - value
			if abs(diff) < self.prec:
				break
			steps = int(diff/self.nmperstep) #TODO: check sign
			print(i, wl, diff, steps)
			#maybe there could also be some sanity check if we are still too far after the first round?
			#set the motion & wait
			self.interwrap([requests['REQ_SET_DELTA'], steps, 0, 1])
			while self.interwrap([requests['REQ_SET_DELTA'], 0, 0, 1])[0] ==1:
				if not self.moving.is_set():
					break
				sleep(0.2) #let's not cause a heavy traffic
			if not self.moving.is_set():
				#stop the motion here
				self.interwrap([requests['REQ_STOP'], 0, 0, 1])
				break
			sleep(1) #We need time to let the wavemeter settle
		self.interwrap([requests['REQ_SET_RELEASE'], 0, 0, 1])
		self.moving.clear()


	@property
	def wavelength(self):
		#check here that nobody is accessing?
		ret = self.interwrap([requests['REQ_GET_WAVELENGTH'], 0, 0, 4])
		return 0 if ret is None else (ret[0] + 256 * ret[1] + 65536 * ret[2])/100.0
	
	@wavelength.setter
	def wavelength(self, value):
		#if it is already moving, disregard
		if self.moving.is_set():
			return
		#also if already there
		if(abs(value - self.wavelength) < self.prec):
			print("release")
			self.interwrap([requests['REQ_SET_RELEASE'], 0, 0, 1])
			return
		#first check if the current wl is already 
		# within precision
		self.moveThread  = Thread(target = self.move, args=(value,))
		self.moving.set()
		self.moveThread.start()
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
		ret = self.interwrap([requests['REQ_SET_DIGI_OUT'], ind, 0, 1])
		#think how to handle the ret value if not connected
		#well it should in general return a list, right?
		if ret is not None:
			self.shut = ind

	@property
	def speed(self):
		ret = self.interwrap([requests['REQ_GET_SPEED'], 0, 0, 2])
		return ret[0] + 256 * ret[1]
	
	@speed.setter
	def speed(self, value):
		ret = self.interwrap([requests['REQ_SET_SPEED'], value, 0, 1])

	@property
	def status(self):
		return 'moving' if self.moving.is_set() else 'stopped'
	
	@status.setter
	def status(self, value):
		if value == 'abort':
			self.moving.clear()
		elif value == 'release':
			if not self.moving.is_set():
				self.interwrap([requests['REQ_SET_RELEASE'], 0, 0, 1])


	
