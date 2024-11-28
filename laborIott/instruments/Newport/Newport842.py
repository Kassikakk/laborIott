from laborIott.instruments.instrument import Instrument



class Newport842(Instrument):
	'''
		Properties are: power (r/o), wl, attenuator, scale 
	'''
	
	def __init__(self, adapter):
		self.wlval = 800
		self.attstate = True
		self.minwl = 400
		self.maxwl = 1100


		super().__init__(adapter, "Newport842")
		#get some initial data
		

	def connect(self):
		if not super().connect():
			return False
		#get some initial data
		sta = self.interact(["*sta\n", True], [""])[0]

		try:
			self.wlval = float(self.parsestats(sta,("Active WaveLength", "nm")))
		except ValueError:
			self.wlval = 800
			
		try:	
			self.attstate = self.parsestats(sta,("Attenuator", "\r"))=='On'
			self.minwl = float(self.parsestats(sta,("Min Wavelength index", '\t')))
			self.maxwl = float(self.parsestats(sta,("Max Wavelength index", '\t')))
		except ValueError:
			self.attstate = True
			self.minwl = 400
			self.maxwl = 1100
		return True

		
	def parsestats(self, stastr, srch):
		#stastr - result of  *sta command
		#srch - tuple (parameter string, endstring)
		s = stastr[stastr.find(srch[0])+len(srch[0])+2:]
		return s[:s.find(srch[1])]
		
		
		
	@property
	def power(self):
		#check if connected here
		pwr = self.interact(["*cvu\n", True], [""])[0]

		try:
			f = float(self.parsestats(pwr,("Current value", "\r")))
			#f = float(pwr[16:-2])  #Ta saadab b'Current value: ... \r\n'
			return f
		except ValueError: #ei saanud floati?
			#return pwr[16:-2] #diagnostiline, aga muidu võib errori visata
			return -1
			
	@property
	def wl(self):
		return self.wlval
	
	@wl.setter
	def wl(self,value):
		if (value < self.minwl) or (value > self.maxwl):
			return
		ret = self.interact(["*swa {}\n".format(value), True],[])[0]
		self.wlval = value
		#if ret != "ACK\r\n": #seems like it doesn't always get ACK
			

			
	@property
	def attenuator(self):
		return self.attstate
	
	@attenuator.setter
	def attenuator(self, value):
		#assume int value, other formats possible
		ivalue = 1 if value else 0
		ret = self.interact(["*atu {}\n".format(ivalue), True],[""])[0]
		self.attstate = value
		#if ret != "ACK\r\n": #seems like it doesn't always get ACK
			
	@property
	def scale(self):
		#ok let's use *sta here for now
		sta = self.interact(["*sta\n", True],[""])[0]

		return (int(self.parsestats(sta,("Current Scale", '\t'))),self.parsestats(sta,("AutoScale", "\r"))=='On')
	
	@scale.setter
	def scale(self, value):
		#assume string value -  accepts 'Auto' and scale strings
		
		ret = self.interact("*ssa {}\n".format(value), [""])[0]
		#print("*ssa {}\n".format(value), ret)
		#if ret == "ACK\r\n":
		#	pass
		
