from laborIott.instruments.instrument import Instrument
from laborIott.validators import strict_discrete_set

class IDus(Instrument):
	'''
	Minimal set: Temperature, Exposure / Accumulation, Spectra, (shutter if no separate Shamrock access)
	'''
	acqmodes = {'single': 1, 'accum': 2, 'kinetics': 3, 'fastkin': 4, 'tillabort': 5}
	errors = {20002: "OK" ,20026: "SpoolErr", 20075: "NoInit", 20072: "Acqring", 20073: "Idle", 20074: "TempCycle", 20013: "ACKError", 20034: "TempOff", 20036: "TempStable", 20035: "TempNotStbl", 20037: "TempNotRchd", 20040: "TempDrift"}
	

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "Andor Idus", **kwargs)
		
		self.acqmode = 'single'
		self.expTimeval = None
		self.noAccval = None
		self.dim = 1024 #size of the image; changed with ReadMode (probly kinetics, too?)
		#neid võib vastavalt vajadusele propertiteks viia
	
	def connect(self):
		if not super().connect():
			return False
		self.interact("Initialize('')")
		self.interact("SetPreAmpGain(1)")#0 - 1x, 1 - 1.7x
		self.interact("SetVSSpeed(3)") #[8.25], 16.25, 32.25, 64.25 (usec/pel)
		#self.interact("SetFilterMode(0)") #0 - no filtering; 2 - cosmic ray removal
		self.interact("SetTriggerMode(0)") #0 Internal; 1 External; 2 External Start (Fast Kin)
		self.interact("SetReadMode(0)") #0 FVB; 1 Multi-Track; 2 Random-track; 3 Single-Track; 4 Image
		

		
	def __del__(self):
		self.interact("ShutDown()")

	@property
	def wavelengths(self):
		return range(1024) 
		
	
	@property
	def temperature(self):
		ret =self.interact("GetTemperature(byref(c_int))")
		print(ret)
		return ["NotConn", -1] if ret is None else [self.errors[ret[0]], ret[1]]
		
	@temperature.setter
	def temperature(self, value):
		if value is None:
			self.interact("CoolerOFF()")
		elif value > -80 and value < 0:
			self.interact("SetTemperature(%d)" % value)
			self.interact("CoolerON()")
	
	@property
	def noAccum(self):
		return self.noAccval
		
	@noAccum.setter
	def noAccum(self, value):
		self.interact("SetNumberAccumulations(%d)" % value)
		#siin võiks, et kui on korras, siis...
		if self.connected:
			self.noAccval = value
		
	@property
	def expTime(self):
		return self.expTimeval
		
	@expTime.setter
	def expTime(self, value):
		self.interact("SetExposureTime(c_float(%g))" % value)
		if self.connected:
			self.expTimeval = value
	
	@property
	def shutter(self):
		return ""

	@shutter.setter
	def shutter(self, value):
		if value =='open':
			self.interact("SetShutter(1,1,0,0)")
		elif value == 'closed':
			self.interact("SetShutter(1,2,0,0)")
	
	'''
	shutter = Instrument.setting("SetShutter(1,%d, 0, 0)", """Switch shutter on/off """,
							  validator=strict_discrete_set,
							  values={'open': 1, 'closed': 2}, map_values=True)
	
	
	acqmode = Instrument.setting("SetAcquisitionMode(%d)", """Set acquisition mode """,
							  validator=strict_discrete_set,
							  values={'single': 1, 'accum': 2, 'kinetics': 3, 'fastkin': 4, 'tillabort': 5}, map_values=True)
	#ilmselt on siin vaja muudki teha, nii et laiendame
	'''
	
	@property
	def acqmode(self):
		return "" #currently returns nothing
	
	@acqmode.setter
	def acqmode(self, value):
		self.interact("SetAcquisitionMode(%d)" % self.acqmodes[value])
		if value == 'single':
			self.interact("SetFilterMode(0)")
		else: #not sure if always? (only single and accum modes are really tested)
			self.interact("SetFilterMode(2)")




	@property
	def status(self):
		ret =self.interact("GetStatus(byref(c_int))")
		return "NotConn" if ret is None else self.errors[ret[1]]
	
	@status.setter
	def status(self, value):
		if value == 'start':
			self.interact("StartAcquisition()")
		elif value == 'abort':
			self.interact("AbortAcquisition()")
			
	@property
	def data(self):
		
		#err, imno = self.interact(["GetTotalNumberImagesAcquired(byref(c_int))"]) #mis sellega oli?
		#See tegelikult ei anna õiget, imno on accum * kin (kui aborditud, siis vähem); peab vaatama, kuidas see õigesti välja nuputada.
		ret = self.interact("GetAcquiredData(byref(c_int*%d), %d)" % (self.dim, self.dim))
		if ret is not None:
			err, out = ret
		else:
			out = []
		#print(self.errors[err])
		return out
	

'''
#general ways to obtain image from SDK
dim = 1024
outlist = []
#Version 1
cimage = (ctypes.c_int * dim)()
err = self._dll.GetAcquiredData(cimage, dim)

#Version 2
#cimageArray = ctypes.c_int * dim
#cimage = cimageArray()
#err = self._dll.GetAcquiredData(ctypes.pointer(cimage), dim)

#for i in range(len(cimage)):
#	outlist.append(cimage[i])

#Version 3 (not working?)
#cimage = (ctypes.c_int * dim)()
#cim = ctypes.cast(cimage, ctypes.POINTER(ctypes.c_int))
#err = self._dll.GetAcquiredData(ctypes.byref(cim), dim)

for p in cimage:
	outlist.append(p)
'''
