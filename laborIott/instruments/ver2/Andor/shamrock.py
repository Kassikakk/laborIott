from laborIott.instruments.instrument import Instrument

success = 20202

class Shamrock(Instrument):

	def __init__(self, adapter, pixelwidth, numpixels, **kwargs):

		self.device = 0 #if we only have one device
		self.numpixels = numpixels
		self.pixelwidth = pixelwidth
		self.wllimits = [None, None]
		super().__init__(adapter, "Shamrock", **kwargs)
				
		#or perhaps we should set pixelwidth and numpixels as properties
		#seeing as we might want to use another camera as well
		#or just give functions to change them (emm...)
		

	def __del__(self):
		self.interact(["ShamrockClose()"])

	def connect(self):
		if not super().connect():
			return False
		
		self.interact(["ShamrockInitialize('')"])
		self.interact(["ShamrockSetPixelWidth({}, c_float({}))".format(self.device,pixelwidth)])
		self.interact(["ShamrockSetNumberPixels({},{})".format(self.device, numpixels)])
		self.grating = self.grating #to set the limits


	@property
	def centerpos(self):
		ret = self.interact(["ShamrockGetWavelength({}, byref(c_float))".format(self.device)])
		return -1 if (ret is None) or (ret[0] != success)  else ret[1]

	@centerpos.setter
	def centerpos(self, val):
		#check by limits
		if (val < self.wllimits[0]) or (val > self.wllimits[1]):
			return
		#it looks like set wl = 0 is equivalent to GotoZeroOrder so no reason to mess with that?
		self.interact(["ShamrockSetWavelength({},c_float({}))".format(self.device, val)])

	'''
	Filter wavelength limits
	1 0.0 11234.0
	2 0.0 5621.0
	3 0.0 0.0
	'''

	@property
	def wavelengths(self):
		#returns an array [numpixels] of wl values
		ret =self.interact(["ShamrockGetCalibration({},byref(c_float*{}),{})".format(self.device,self.numpixels, self.numpixels)])
		return [0,1] if (ret is None) or (ret[0] != success)  else ret[1]

	#wavelengths - OK
	#centerpos NB 0 supported - OK
	
	@property
	def slit(self):
		ret =self.interact(["ShamrockGetAutoSlitWidth({}, 1, byref(c_float))".format(self.device)])
		return -1 if (ret is None) or (ret[0] != success)  else ret[1]
		

	@slit.setter
	def slit(self, val):
		#we should check val limits here
		self.interact(["ShamrockSetAutoSlitWidth({}, 1, c_float({}))".format(self.device, val)])
	
	@property
	def gratingdict(self):
		dictout = {}
		nofilts = self.interact(["ShamrockGetNumberGratings({}, byref(c_int))".format(self.device)])[1]
		for i in range(nofilts):
			#filter numbering is 1-based
			ret = self.interact(["ShamrockGetGratingInfo({}, {},byref(c_float), byref(c_char*4), byref(c_int),byref(c_int))".format(self.device,i+1)])
			desc = "{} l/mm ".format(int(ret[1] + 0.5))
			#format the blaze value (max 4 chars) and add to the description
			for s in ret[2]:
				if ord(s) == 0:
					break
				desc += bytes.decode(s)
			dictout[desc] = i + 1
		return dictout
	
	@property
	def grating(self):
		ret = self.interact(["ShamrockGetGrating({}, byref(c_int))".format(self.device)])
		return ret[1] if ret[0] == success  else None

	@grating.setter
	def grating(self, val):
		self.interact(["ShamrockSetGrating({}, {})".format(self.device, val)])
		#set the limits
		ret =self.interact(["ShamrockGetWavelengthLimits({},{},byref(c_float),byref(c_float))".format(self.device,val)])
		self.wllimits = [ret[1],ret[2]]

	@property
	def flipper(self):
		ret = self.interact(["ShamrockGetFlipperMirror({}, 2, byref(c_int))".format(self.device)])
		return ('direct', 'side')[ret[1]] if ret[0] == success  else None

	@flipper.setter
	def flipper(self, val):
		try:
			#only accept these two values
			ind = ('direct', 'side').index(val)
		except ValueError:
			return
		self.interact(["ShamrockSetFlipperMirror({}, 2, {})".format(self.device, ind)])

	@property
	def shutter(self):
		ret = self.interact(["ShamrockGetShutter({}, byref(c_int))".format(self.device)])
		return ('closed','open')[ret[1]] if ret[0] == success  else None

	@shutter.setter
	def shutter(self, val):
		try:
			#only accept these two values
			ind = ('closed','open').index(val)
		except ValueError:
			return
		self.interact(["ShamrockSetShutter({}, {})".format(self.device, ind)])

