from laborIott.instrument import Instrument
from laborIott.validators import strict_discrete_set
from pandas import read_csv
from scipy.interpolate import interp1d
from struct import unpack
import os

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class ChiraScan(Instrument):
	'''
	Minimal set: shutter, position, bandwidth
	'''
	

	def __init__(self, adapter, **kwargs):
		'''
		Kuidagi peaks vist mingit paralleelarvestust pidama positioni ja bandwidthi üle?
		'''
		super().__init__(adapter, "Chirascan", **kwargs)
		#parse calibration file
		d=read_csv(localPath("MonoCal.conf"), skiprows=7, skipfooter=1, engine='python', header = None)
		#problem is here it tends to interpret program's directory as current
		self.f1 = interp1d(d.loc[:,0], d.loc[:,1]) #use int(self.f1(wl)) to get number of steps
		self.f2 = interp1d(d.loc[:,0], d.loc[:,3]) #use int(self.f2(wl)*bw) to get number of steps for stepper 2
		#do some initialization
		self.write("PiStar_initialise()")
		self.write("PiStar_command(c_uint(3),c_uint(0x3020),c_short(3),c_short(0),c_short(0),c_short(0),c_short(0),c_short(0))")
		self.shutter = 'closed'
		self.wl = 1000.0
		self.bw = 1.0
		#set wavelength which also sets bandwidth
		self.wavelength = 1000.0
		
	
	
	shutter = Instrument.setting("PiStar_command(c_uint(3),c_uint(0x301f),c_short(3),c_short(%d),c_short(0),c_short(0),c_short(0),c_short(0))", """Switch shutter on/off """,
							  validator=strict_discrete_set,
							  values={'open': 0x1748, 'closed': 0x63}, map_values=True)
							  
	@property
	def wavelength(self):
		return self.wl
	
	@wavelength.setter
	def wavelength(self, value):
		#check value between 160 and 1380something
		if (value < 160) or (value > 1385):
			return
		#correct the value, incl for temperature
		#just some results from square polynome fitting
		a = 4.5-0.016*value+4.5e-5*value**2
		b = 0.05-0.00005*value-1.21e-6*value**2
		dval = a + b*self.monotemp
		#print(self.monotemp,value,dval,value-dval,self.f1(value-dval))
		motor1 = int(self.f1(value-dval))
		if motor1 > 65535:
			motor1 -= 65535
			ovfl = 1
		else:
			ovfl = 0
			
		motor2 = int(self.f2(value)*self.bw)
		self.write("PiStar_command(c_uint(3),c_uint(0x301f),c_short(2),c_short(%d),c_short(0),c_short(0),c_short(0),c_short(0))" % motor2)

		self.write("PiStar_command(c_uint(3),c_uint(0x301f),c_short(1),c_short(%d),c_short(%d),c_short(0),c_short(0),c_short(0))" % (motor1, ovfl))
		self.wl = value

	@property
	def bandwidth(self):
		return self.bw
	
	@bandwidth.setter
	def bandwidth(self, value):
		#what are the limits?
		if (value < 0) or (value > 10):
			return
		motor2 = int(self.f2(self.wl)*value)
		self.write("PiStar_command(c_uint(3),c_uint(0x301f),c_short(2),c_short(%d),c_short(0),c_short(0),c_short(0),c_short(0))" % motor2)
		self.bw = value
		
	@property
	def stepsmissing(self):
		#request location and target data from ChiraScan memory section 2/1
		err,sdata,num =self.values("PiStar_status(c_uint(3),c_short(0x3002),c_short(2),c_short(1),byref(c_char*0x200),byref(c_uint))")
		#we only need sdata
		#join is needed to convert (list of bytes) to (string of bytes)
		loc2 = unpack('LL',b''.join(sdata[0x15e:0x166]))
		loc1 = unpack('LL',b''.join(sdata[0x198:0x1a0]))
		#these will be tuples of (currentsteps, targetsteps), so we calculate their differences
		return (loc1[1]-loc1[0], loc2[1]-loc2[0])
		
	@property
	def monotemp(self):
		#request monochromator inner temperature from ChiraScan memory section 1/0
		#it appears that short (2B) int at offset 0x17c carries this information
		err,sdata,num =self.values("PiStar_status(c_uint(3),c_short(0x3002),c_short(1),c_short(0),byref(c_char*0x200),byref(c_uint))")
		#we only need sdata
		#join is needed to convert (list of bytes) to (string of bytes)
		temp = unpack('H',b''.join(sdata[0x17c:0x17e]))
		#coefficients obtained from lin. regression (+-0.15 deg or so)
		return -100.4 + 0.049 * temp[0] 
	
	@property
	def cuvettetemp(self):
		#request cuvette sensor temperature from ChiraScan memory section 1/0
		#it appears that short (2B) int at offset 0x184 carries this information
		err,sdata,num =self.values("PiStar_status(c_uint(3),c_short(0x3002),c_short(1),c_short(0),byref(c_char*0x200),byref(c_uint))")
		#we only need sdata
		#join is needed to convert (list of bytes) to (string of bytes)
		temp = unpack('H',b''.join(sdata[0x184:0x186]))
		#coefficients obtained from lin. regression (+-0.15 deg or so)
		return -103 + 0.05 * temp[0] 
