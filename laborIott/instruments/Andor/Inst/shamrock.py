from laborIott.instrument import Instrument

success = 20202

class Shamrock(Instrument):

	def __init__(self, adapter, pixelwidth, numpixels, **kwargs):
		super().__init__(adapter, "Shamrock", **kwargs)
		self.write("ShamrockInitialize('')")
		self.device = 0 #if we only have one device
		#or perhaps we should set pixelwidth and numpixels as properties
		#seeing as we might want to use another camera as well
		self.write("ShamrockSetPixelWidth({}, c_float({}))".format(self.device,pixelwidth))
		self.numpixels = numpixels
		self.write("ShamrockSetNumberPixels({},{})".format(self.device, numpixels))
		

	def __del__(self):
		self.write("ShamrockClose()")

	@property
	def centerpos(self):
		ret = self.values("ShamrockGetWavelength({}, byref(c_float))".format(self.device))
		return ret[1] if ret[0] == success  else ret[0] #kuigi none pole vist väga hea?

	@centerpos.setter
	def centerpos(self, val):
		#check by limits
		#it looks like set wl = 0 is equivalent to GotoZeroOrder so no reason to mess with that?
		self.write("ShamrockSetWavelength({},c_float({}))".format(self.device, val))

	'''
	Filter wavelength limits
	0 0.0 0.0
	1 0.0 11234.0
	2 0.0 5621.0
	'''

	@property
	def wavelengths(self):
		#returns an array [numpixels] of wl values
		ret =self.values("ShamrockGetCalibration({},byref(c_float*{}),{})".format(self.device,self.numpixels, self.numpixels))
		return ret[1]
	#wavelengths - OK
	#centerpos NB 0 supported - OK
	#slit
	#grating 
	#	ret =self.values("ShamrockGetWavelengthLimits({},{},byref(c_float),byref(c_float))".format(self.device,grating))
	#gratingdict
	#flipper
	#shutter vist ka siis (vinst overrideb selle)