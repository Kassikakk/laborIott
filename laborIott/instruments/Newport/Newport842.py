from laborIott.instruments.instrument import Instrument



class Newport842(Instrument):
	'''
		Properties are: power (r/o), wl, attenuator, scale 
	'''
	pwr_scales = ["opt","1pW", "3pW", "10pW", "30pW", "100pW", "300pW", "1nW", "3nW", "10nW", "30nW", "100nW",
			    "300nW", "1uW", "3uW", "10uW", "30uW", "100uW", "300uW", "1mW", "3mW", "10mW", "30mW", "100mW", 
				"300mW", "1W", "3W", "10W", "30W", "100W", "300W"]

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
		sta = self.interact(["*sta\n", 3], [""])
		

		try:
			self.wlval = float(self.parsestats(sta[0],("Active WaveLength", "nm")))
		except ValueError:
			self.wlval = 800
			
		try:	
			self.attstate = self.parsestats(sta[1],("Attenuator", "\r"))=='On'
			self.minwl = float(self.parsestats(sta[0],("Min Wavelength index", '\t')))
			self.maxwl = float(self.parsestats(sta[0],("Max Wavelength index", '\t')))
		except ValueError:
			self.attstate = True
			self.minwl = 400
			self.maxwl = 1100
		return True

		
	def parsestats(self, stastr, srch):
		#stastr - result of  *sta command
		#srch - tuple (parameter string, endstring)
		if stastr.find(srch[0]) < 0:
			print ("Cannot find parameter {} in {}".format(srch[0], stastr))
			return -1
		s = stastr[stastr.find(srch[0])+len(srch[0])+2:]
		return s[:s.find(srch[1])]
		
		
		
	@property
	def power(self):
		#check if connected here
		pwr = self.interact(["*cvu\n", 1], [""])[0]

		try:
			f = float(self.parsestats(pwr,("Current Value", "\r")))
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
		ret = self.interact(["*swa {}\n".format(value), 1],[])[0]
		self.wlval = value
		#if ret != "ACK\r\n": #seems like it doesn't always get ACK
			

			
	@property
	def attenuator(self):
		return self.attstate
	
	@attenuator.setter
	def attenuator(self, value):
		#assume int value, other formats possible
		ivalue = 1 if value else 0
		ret = self.interact(["*atu {}\n".format(ivalue), 1],[""])[0]
		self.attstate = value
		#if ret != "ACK\r\n": #seems like it doesn't always get ACK
			
	@property
	def scale(self):
		#ok let's use *sta here for now
		sta = self.interact(["*sta\n", 3],[""])
		#print(sta)
		#return(0,True)
		scalenum = int(self.parsestats(sta[0],("Current Scale", '\t')))
		
		return (self.pwr_scales[scalenum],self.parsestats(sta[2],("AutoScale", "\r"))=='On')
	
	@scale.setter
	def scale(self, value):
		#assume string value -  accepts 'Auto' and scale strings
		
		ret = self.interact(["*ssa {}\n".format(value),1], [""])[0]
		#print("*ssa {}\n".format(value), ret)
		#if ret == "ACK\r\n":
		#	pass

	@property
	def headtype(self):
		#returns the type of the head, e.g. '818P'
		sta = self.interact(["*sta\n", 3],[""])[0]
		interim = self.parsestats(sta,("Head Serial Number", "\r"))
		t1 = interim.find('\t')
		t2 = interim.find('\t', t1+1)
		#print("Headtype interim", interim, t1, t2)
		return interim[t1+1:t2] + "(S/N:" + interim[:t1] + ")" if t1 >= 0 and t2 >= 0 else "Unknown"
