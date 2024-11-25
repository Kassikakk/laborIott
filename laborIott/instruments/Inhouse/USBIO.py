from laborIott.instruments.instrument import Instrument
from pandas import read_csv
from scipy.interpolate import interp1d
import os

from time import sleep

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

requests = { 'REQ_ECHO':0,'REQ_SET_PINS' : 1, 'REQ_GET_PINS' : 2, 'REQ_SET_PWM_FRQ' : 3, 
'REQ_GET_PWM_FRQ' : 4, 'REQ_SET_PWM_DUTY' : 5, 'REQ_GET_PWM_DUTY' : 6}


class USBIO(Instrument):
	'''
	This class refers to V-USB connected USBIO, connecting

	'''


	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "USBIO", **kwargs)
		#OD wheel servo constants
		#self.ODperDeg = 0.0148
		#self.degperProc = 28.0 #but it depends on freq
		#self.msperDeg = 8.0
		d=read_csv(localPath("ODcalib.txt"), sep='\t')
		self.ODlimits = (min(d['OD']), max(d['OD']))
		self.duty2OD = interp1d(d['duty'], d['OD']) 
		self.OD2duty = interp1d(d['OD'], d['duty'])




	#what we need:
	#bits (7) - may be wrapped
	#servo freq
	#servo duty
	#(servo release?)
	
	def getpin(self, pinno):
		if (pinno >= 0) and (pinno < 11):
			ret = self.interact([requests['REQ_GET_PINS'],0,pinno,1])
			return -1 if ret is None else ret[0]

	def setpin(self, pinno, val):
		if (pinno >= 0) and (pinno < 7):
			self.interact([requests['REQ_SET_PINS'],(val != 0),pinno,1])

	@property
	def freq1(self):
		#freq1 is the frequency for PWM 0 and 1
		ret = self.interact([requests['REQ_GET_PWM_FRQ'],0,1,2])
		return -1 if ret is None else ret[0] + ret[1]*256
	
	@freq1.setter
	def freq1(self, value):
		if value > 0:
			self.interact([requests['REQ_SET_PWM_FRQ'],value,1,1])
		

	@property
	def freq2(self):
		#freq2 is the frequency for PWM 2
		ret = self.interact([requests['REQ_GET_PWM_FRQ'],0,2,2])
		return -1 if ret is None else ret[0] + ret[1]*256
	
	@freq2.setter
	def freq2(self, value):
		if value > 0:
			self.interact([requests['REQ_SET_PWM_FRQ'],value,2,1])
		
	@property
	def duty0(self):
		ret = self.interact([requests['REQ_GET_PWM_DUTY'],0,0,2])
		return -1 if ret is None else ret[0] + ret[1]*256
	
	@duty0.setter
	def duty0(self, value):
		if value > 0:
			self.interact([requests['REQ_SET_PWM_DUTY'],value,0,1])

	@property
	def OD(self):
		try:
			ret = self.duty2OD(self.duty0)
		except ValueError:
			return -1
		return ret
	
	@OD.setter
	def OD(self, value):
		#do the calcs
		if  value >= self.ODlimits[0] and value <= self.ODlimits[1]:
			self.duty0 = int(self.OD2duty(value))
		

	@property
	def duty1(self):
		ret = self.interact([requests['REQ_GET_PWM_DUTY'],0,1,2])
		return -1 if ret is None else ret[0] + ret[1]*256
	
	@duty1.setter
	def duty1(self, value):
		if value > 0:
			self.interact([requests['REQ_SET_PWM_DUTY'],value,1,1])
		
	
	@property
	def duty2(self):
		ret = self.interact([requests['REQ_GET_PWM_DUTY'],0,2,2])
		return -1 if ret is None else ret[0] + ret[1]*256
	
	@duty2.setter
	def duty2(self, value):
		if value > 0:
			self.interact([requests['REQ_SET_PWM_DUTY'],value,2,1])
