from .andor import IDus 



class IDusKymera(IDus):
	
	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, **kwargs)
		#at this point we can expect that the camera is initialized
		
		
		
		
	def __del__(self):
		super().__del__()
		
	def command(self, comstr):
		
		instr = "I2CBurstWrite(c_char(88),c_long(%d),c_char_p(b'%s\\r'))" % (len(comstr)+1,comstr)
		#print(instr)
		self.interact(instr)
		#now we need to read the answer until OK\r
		chkstr = b"OK\r"
		ri = 0 #running index
		output = b''
		for i in range(500):
			ret = self.interact("I2CBurstRead(c_char(88),c_long(2),byref(c_char * 2))")
			if ret is None:
				break
			output+=ret[1][1]
			if (ret[1][1][0] == chkstr[ri]):
				ri += 1
				if ri == len(chkstr):
					break
			elif (ret[1][1][0] == chkstr[0]): #kas see ikka lahendab olukorra?
				ri = 1
			else:
				ri = 0
		return output
		
	@property
	def wavelengths(self):
		#empirical right now
		centerwl = self.centerpos
		if centerwl == 0:
			return range(1024)
		#else
		if self.grating == 1: #150 /mm
			a1 = 0.8610393 - 1.85707E-5 * centerwl - 2.62137E-9 * (centerwl ** 2)
			a2 = -1.0598E-5 - 4.545E-9 * centerwl
			a3 = -7.78e-9
		else: #300 /mm
			a1 = 0.4304967 - 1.84871E-5 * centerwl - 5.32032E-9 * (centerwl ** 2)
			a2 = -5.3224E-6 - 4.5E-9 * centerwl
			a3 = -3.82e-9
		return [centerwl + a1 * p + a2 * p**2 + a3*p**3 for p in range(-511,513)]
		
	@property
	def centerpos(self):
		for i in range(5): #try several times
			s = self.command("POSITION?")
			if s.startswith(b"POSITION"):
				break
		try:
			val = float(s[9:-4]) #strip POSITION+spc and \rOK\r
		except ValueError:
			return -1
		return val
		
	@centerpos.setter
	def centerpos(self, val):
		#any maxvalue known?
		if val < 0 or val > 1000:
			return
		self.command("MOVETO %.03f" % val)
		while abs(self.centerpos - val) > 0.1: #what's the step?
			pass
	
	@property
	def filter(self):
		for i in range(5): #try several times
			s = self.command("FILTER?")
			if s.startswith(b"FILTER"):
				break
		try:
			val = int(s[7:-4]) #strip FILTER+spc and \rOK\r
		except ValueError:
			return -1
		return val
		
	@filter.setter
	def filter(self, val):

		if val < 1 or val > 6:
			return
		self.command("FILTER %d" % val)
		while self.filter != val:
			pass
			
	@property
	def filterdict(self):
		dictout = {}
		for i in range(6):
			for j in range(5):
				s = self.command("CONFIG_SYSTEM_DATA? %d" % (82 + i))
				loc = s.find(b"CONFIG_SYSTEM_DATA %d" % (82 + i))
				if loc > -1:
					break
				
			dictout[s[loc + 22:-4].decode()] = i+1
		return dictout
		
	@property
	def focus(self):
		for i in range(5): #try several times
			s = self.command("FOCUS?")
			if s.startswith(b"FOCUS"):
				break
		try:
			val = int(s[6:-4]) #strip FOCUS+spc and \rOK\r
		except ValueError:
			return -1
		return val
		
	@focus.setter
	def focus(self, val):

		if val < 0 or val > 600: #FOCUS_TOTALSTEPS? gives 600
			return
		curfoc = self.focus
		#first is direction (0-increase, 1 - decrease) and second is num of steps
		self.command("MOVE_FOCUS %d,%d" % (int(val < curfoc), abs(val-curfoc)))
		while self.focus != val:
			pass
			
	@property
	def grating(self):
		for i in range(5): #try several times
			s = self.command("GRATING?")
			if s.startswith(b"GRATING"):
				break
		try:
			val = int(s[8:-4]) #strip GRATING+spc and \rOK\r
		except ValueError:
			return -1
		return val
		
	@grating.setter
	def grating(self, val):

		if val < 1 or val > 3:
			return
		self.command("GRATING %d" % val)
		while self.grating != val:
			pass
			
			
	@property
	def gratingdict(self):
		dictout = {}
		for i in range(5):
			s = self.command("GRATINGS?")
			loc = s.find(b"GRATINGS")
			if loc > -1:
				break
		gratlist = s[loc + 10:-4].split(b"\r\n")
		for g in gratlist:
			sublist = g.split(b',')
			try:
				ind = int(sublist[0])
				desc = "%d l/mm %s" % (int(float(sublist[1])), sublist[2].decode())
				dictout[desc] = ind #still not sure which way is good?
			except ValueError:
				pass
		return dictout
