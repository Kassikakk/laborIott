from laborIott.instrument import Instrument
from laborIott.validators import strict_discrete_set

class IDus(Instrument):
	'''
	Minimal set: Temperature, Exposure / Accumulation, Spectra, (shutter if no separate Shamrock access)
	'''
	acqmodes = {'single': 1, 'accum': 2, 'kinetics': 3, 'fastkin': 4, 'tillabort': 5}
	errors = {20002: "OK" ,20026: "SpoolErr", 20075: "NoInit", 20072: "Acqring", 20073: "Idle", 20074: "TempCycle", 20013: "ACKError", 20034: "TempOff", 20036: "TempStable", 20035: "TempNotStbl", 20037: "TempNotRchd", 20040: "TempDrift"}
	

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "Andor Idus", **kwargs)
		self.write("Initialize('')")
		self.write("SetPreAmpGain(1)")#0 - 1x, 1 - 1.7x
		self.write("SetVSSpeed(3)") #[8.25], 16.25, 32.25, 64.25 (usec/pel)
		#self.write("SetFilterMode(0)") #0 - no filtering; 2 - cosmic ray removal
		self.write("SetTriggerMode(0)") #0 Internal; 1 External; 2 External Start (Fast Kin)
		self.write("SetReadMode(0)") #0 FVB; 1 Multi-Track; 2 Random-track; 3 Single-Track; 4 Image
		self.acqmode = 'single'
		self.expTimeval = None
		self.noAccval = None
		self.dim = 1024 #size of the image; changed with ReadMode (probly kinetics, too?)
		#neid võib vastavalt vajadusele propertiteks viia

		
	def __del__(self):
		self.write("ShutDown()")
		
	@property
	def wavelengths(self):
		return range(1024) #?laiendame seda hiljem
	
	@property
	def temperature(self):
		ret =self.values("GetTemperature(byref(c_int))")
		return self.errors[ret[0]], ret[1]
		
	@temperature.setter
	def temperature(self, value):
		if value is None:
			self.write("CoolerOFF()")
		elif value > -80 and value < 0:
			self.write("SetTemperature(%d)" % value)
			self.write("CoolerON()")
	
	@property
	def noAccum(self):
		return self.noAccval
		
	@noAccum.setter
	def noAccum(self, value):
		self.write("SetNumberAccumulations(%d)" % value)
		#siin võiks, et kui on korras, siis...
		self.noAccval = value
		
	@property
	def expTime(self):
		return self.expTimeval
		
	@expTime.setter
	def expTime(self, value):
		self.write("SetExposureTime(c_float(%g))" % value)
		self.expTimeval = value
	
	
	shutter = Instrument.setting("SetShutter(1,%d, 0, 0)", """Switch shutter on/off """,
							  validator=strict_discrete_set,
							  values={'open': 1, 'closed': 2}, map_values=True)
	
	'''
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
		self.write("SetAcquisitionMode(%d)" % self.acqmodes[value])
		if value == 'single':
			self.write("SetFilterMode(0)")
		else: #not sure if always? (only single and accum modes are really tested)
			self.write("SetFilterMode(2)")




	@property
	def status(self):
		ret =self.values("GetStatus(byref(c_int))")
		return self.errors[ret[1]]
	
	@status.setter
	def status(self, value):
		if value == 'start':
			self.write("StartAcquisition()")
		elif value == 'abort':
			self.write("AbortAcquisition()")
			
	@property
	def data(self):
		
		err, imno = self.values("GetTotalNumberImagesAcquired(byref(c_int))")
		#See tegelikult ei anna õiget, imno on accum * kin (kui aborditud, siis vähem); peab vaatama, kuidas see õigesti välja nuputada.
		err, out = self.values("GetAcquiredData(byref(c_int*%d), %d)" % (self.dim, self.dim))
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
