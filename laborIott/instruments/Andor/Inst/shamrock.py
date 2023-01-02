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
		self.wllimits = [None, None]
		self.grating = self.grating #to set the limits
		

	def __del__(self):
		self.write("ShamrockClose()")

	@property
	def centerpos(self):
		ret = self.values("ShamrockGetWavelength({}, byref(c_float))".format(self.device))
		return ret[1] if ret[0] == success  else None #kuigi none pole vist väga hea?

	@centerpos.setter
	def centerpos(self, val):
		#check by limits
		if (val < self.wllimits[0]) or (val > self.wllimits[1]):
			return
		#it looks like set wl = 0 is equivalent to GotoZeroOrder so no reason to mess with that?
		self.write("ShamrockSetWavelength({},c_float({}))".format(self.device, val))

	'''
	Filter wavelength limits
	1 0.0 11234.0
	2 0.0 5621.0
	3 0.0 0.0
	'''

	@property
	def wavelengths(self):
		#returns an array [numpixels] of wl values
		ret =self.values("ShamrockGetCalibration({},byref(c_float*{}),{})".format(self.device,self.numpixels, self.numpixels))
		return ret[1]
	#wavelengths - OK
	#centerpos NB 0 supported - OK
	
	@property
	def slit(self):
		ret =self.values("ShamrockGetAutoSlitWidth({}, 1, byref(c_float))".format(self.device))
		return ret[1] if ret[0] == success  else ret[0]

	@slit.setter
	def slit(self, val):
		#we should check val limits here
		self.write("ShamrockSetAutoSlitWidth({}, 1, c_float({}))".format(self.device, val))
	
	@property
	def gratingdict(self):
		dictout = {}
		nofilts = self.values("ShamrockGetNumberGratings({}, byref(c_int))".format(self.device))[1]
		print(nofilts)
		for i in range(nofilts):
			#filter numbering is 1-based
			ret = self.values("ShamrockGetGratingInfo({}, {},byref(c_float), byref(c_char*4), byref(c_int),byref(c_int))".format(self.device,i+1))
			desc = "{} l/mm ".format(int(ret[1] + 0.5))
			for s in ret[2]:
				if ord(s) == 0:
					break
				desc += bytes.decode(s)
			dictout[desc] = i + 1
		return dictout
	
	@property
	def grating(self):
		ret = self.values("ShamrockGetGrating({}, byref(c_int))".format(self.device))
		return ret[1] if ret[0] == success  else None

	@grating.setter
	def grating(self, val):
		self.write("ShamrockSetGrating({}, {})".format(self.device, val))
		#set the limits
		ret =self.values("ShamrockGetWavelengthLimits({},{},byref(c_float),byref(c_float))".format(self.device,val))
		self.wllimits = [ret[1],ret[2]]

	@property
	def flipper(self):
		ret = self.values("ShamrockGetFlipperMirror({}, 2, byref(c_int))".format(self.device))
		return ret[1] if ret[0] == success  else None

	@flipper.setter
	def flipper(self, val):
		 self.write("ShamrockSetFlipperMirror({}, 2, {})".format(self.device, val))
	#slit - OK
	#grating - OK
	#gratingdict - OK
	#flipper
	#shutter vist ka siis (vinst overrideb selle)
