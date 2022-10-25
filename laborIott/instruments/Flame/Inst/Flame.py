from laborIott.instrument import Instrument
from laborIott.validators import strict_discrete_set
from ctypes import POINTER, Structure, c_int, c_double, addressof
from threading import Thread, Event

class DblArr(Structure):
	_fields_ = [("len", c_int),("data", POINTER(c_double))]


class Flame(Instrument):

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "Flame", **kwargs)
		
		self.handle = self.values("Wrapper_Create()")[0]
		self.no = self.values("Wrapper_openAllSpectrometers(%d)" % self.handle)[0]
		#self.no == 0, siis pole midagi taga.
		if self.no > 0:
			self.minExpTime = self.values("Wrapper_getMinimumIntegrationTime(%d, 0)" % self.handle)[0]
		self.spectrum = []
		self.acquiring = Event()
		self.dataReady = Event()

	def __del__(self):
		self.write("Wrapper_closeAllSpectrometers(%d)" % self.handle)
		self.write("Wrapper_Destroy(%d)" % self.handle)
		
	@property
	def expTime(self):
		return self.values("Wrapper_getIntegrationTime(%d,0)" % self.handle)[0] / 1.0e6
	
	@expTime.setter
	def expTime(self,value):
		#value is in seconds now, count to micros
		intvalue = int(value * 1e6)
		#check if less than minimum
		if (intvalue > self.minExpTime) and (self.no > 0):
			self.write("Wrapper_setIntegrationTime(%d,0,%d)" % (self.handle,intvalue))
			
	@property
	def noAccum(self):
		return self.values("Wrapper_getScansToAverage(%d,0)" % self.handle)[0]
	
	@noAccum.setter
	def noAccum(self,value):
		if (self.no > 0):
			self.write("Wrapper_setScansToAverage(%d,0,%d)" % (self.handle,value))
	
	@property
	def corrElDark(self):
		return self.values("Wrapper_getCorrectForElectricalDark(%d,0)" % self.handle)[0]
	
	@corrElDark.setter
	def corrElDark(self,value):
		if (self.no > 0):
			if value == 'on':
				self.write("Wrapper_setCorrectForElectricalDark(%d,0,%d)" % (self.handle,1))
			elif value == 'off':
				self.write("Wrapper_setCorrectForElectricalDark(%d,0,%d)" % (self.handle,0))
		
	def readData(self): #thread function to read spectrum
		darr = DblArr()
		self.write("Wrapper_getSpectrum(%d,0,%d)" % (self.handle,addressof(darr)))
		self.spectrum = [darr.data[i] for i in range(darr.len)]
		self.dataReady.set()
		self.acquiring.clear()
		
	@property
	def wavelengths(self):
		if self.no > 0:
			darr = DblArr()
			self.write("Wrapper_getWavelengths(%d,0,%d)" % (self.handle,addressof(darr)))
			return [darr.data[i] for i in range(darr.len)]
		else:
			return []
			
	@property
	def asyncready(self): #returns async properties ready to be read
		return ['data'] if self.dataReady.isSet() else []

	@property
	def status(self):
		return 'acqring' if self.acqring.isSet() else 'idle'
	
	@status.setter
	def status(self, value):
		if value == 'start':
			self.readThread  = Thread(target = self.readData)
			self.acquiring.set()
			self.readThread.start()

			#set event ja stardi thread
		#elif value == 'abort':
		#	self.write("AbortAcquisition()") #kas saab selle abortida? (stoppable)
		
	@property
	def data(self):
		if self.acquiring.isSet():
			return []
		elif self.dataReady.isSet():
			self.dataReady.clear()
			return self.spectrum
		else:
			return []
