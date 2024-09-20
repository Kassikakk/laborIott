from laborIott.instruments.instrument import Instrument
#from laborIott.validators import strict_discrete_set
from ctypes import POINTER, Structure, c_int, c_double, addressof
from threading import Thread, Event

class DblArr(Structure):
	_fields_ = [("len", c_int),("data", POINTER(c_double))]


class Flame(Instrument):

	'''
	Flame spectrometer instrument
	Assumed main adapter is SDKAdapter
	with following on path:
		for win32:
			OmniDriver32.dll (main library, windll)
			common32.dll (dependency)
		for win64:
			OmniDriver64.dll (main library, windll)
			common64.dll (dependency)
		for linux32:
			libOmniDriver.so
			libcommon.so
		for some strange reason, linux64 is not supported
	some background installation may also be needed (?), refer to OmniDriver setup.
	TODO: Need to guard against asking (anything) during the acquiring?

	'''

	def __init__(self, adapter):
		
		self.handle = 0
		self.no = 0
		#self.no == 0, siis pole midagi taga.
		self.minExpTime = 0
		super().__init__(adapter, "Flame")
		#TODO: Change this when we correct adapter error handling
		self.spectrum = []
		self.acquiring = Event()
		self.dataReady = Event()

	def connect(self):
		if not super().connect():
			return False
		self.handle = self.interact("Wrapper_Create()", [0])[0]
		self.no = self.interact("Wrapper_openAllSpectrometers(%d)" % self.handle, [0])[0]
		self.minExpTime = self.interact("Wrapper_getMinimumIntegrationTime(%d, 0)" % self.handle,[0])[0]

		

	def __del__(self):
		self.interact("Wrapper_closeAllSpectrometers(%d)" % self.handle)
		self.interact("Wrapper_Destroy(%d)" % self.handle)
		
	@property
	def expTime(self):
		return self.interact("Wrapper_getIntegrationTime(%d,0)" % self.handle,[0])[0] / 1.0e6
	
	@expTime.setter
	def expTime(self,value):
		#value is in seconds now, count to micros
		intvalue = int(value * 1e6)
		#check if less than minimum
		if (intvalue > self.minExpTime) and (self.no > 0):
			self.interact("Wrapper_setIntegrationTime(%d,0,%d)" % (self.handle,intvalue))
			
	@property
	def noAccum(self):
		return self.interact("Wrapper_getScansToAverage(%d,0)" % self.handle,[1])[0]
	
	@noAccum.setter
	def noAccum(self,value):
		if (self.no > 0):
			self.interact("Wrapper_setScansToAverage(%d,0,%d)" % (self.handle,value))
	
	@property
	def corrElDark(self):
		return self.interact("Wrapper_getCorrectForElectricalDark(%d,0)" % self.handle,[0])[0]
	
	@corrElDark.setter
	def corrElDark(self,value):
		if (self.no > 0):
			if value == 'on':
				self.interact("Wrapper_setCorrectForElectricalDark(%d,0,%d)" % (self.handle,1))
			elif value == 'off':
				self.interact("Wrapper_setCorrectForElectricalDark(%d,0,%d)" % (self.handle,0))
		
	def readData(self): #thread function to read spectrum
		darr = DblArr()
		self.interact("Wrapper_getSpectrum(%d,0,%d)" % (self.handle,addressof(darr)))
		self.spectrum = [darr.data[i] for i in range(darr.len)]
		self.dataReady.set()
		self.acquiring.clear()
		
	@property
	def wavelengths(self):
		darr = DblArr()
		#TODO:what do we get here if success / not? Also in readData
		if self.interact("Wrapper_getWavelengths(%d,0,%d)" % (self.handle,addressof(darr)),[0])[0]:
			return [darr.data[i] for i in range(darr.len)]
		else:
			return [0,1]
	'''		
	@property
	def asyncready(self): #returns async properties ready to be read
		return ['data'] if self.dataReady.isSet() else []
	'''

	@property
	def status(self):
		return 'Acqring' if self.acquiring.isSet() else 'idle'
	
	@status.setter
	def status(self, value):
		if value == 'start':
			self.readThread  = Thread(target = self.readData)
			self.acquiring.set()
			self.readThread.start()

			#set event ja stardi thread
		#elif value == 'abort':
		#	self.interact("AbortAcquisition()") #kas saab selle abortida? (stoppable)
		
	@property
	def data(self):
		if self.acquiring.isSet():
			return []
		elif self.dataReady.isSet():
			self.dataReady.clear()
			return self.spectrum
		else:
			return []
