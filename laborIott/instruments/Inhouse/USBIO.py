from laborIott.instruments.instrument import Instrument

from time import sleep

requests = { 'REQ_ECHO':0,'REQ_SET_PINS' : 1, 'REQ_GET_PINS' : 2, 'REQ_SET_PWM_FRQ' : 3, 
'REQ_GET_PWM_FRQ' : 4, 'REQ_SET_PWM_DUTY' : 5, 'REQ_GET_PWM_DUTY' : 6}


class USBIO(Instrument):
	'''
	This ver2 class refers to V-USB connected USBIO, connecting

	'''


	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "USBIO", **kwargs)
		#OD wheel servo constants
		self.ODperDeg = 0.0148
		self.degperProc = 28.0
		self.msperDeg = 8.0



	#what we need:
	#bits (7) - may be wrapped
	#servo freq
	#servo duty
	#(servo release?)
	
	def getpin(self, pinno):
		if (pinno >= 0) and (pinno < 11):
			return self.interact([requests['REQ_GET_PINS'],0,pinno,1])[0]

	def setpin(self, pinno, val):
		if (pinno >= 0) and (pinno < 7):
			return self.interact([requests['REQ_SET_PINS'],(val != 0),pinno,1])[0]

	@property
	def freq1(self):
		#freq1 is the frequency for PWM 0 and 1
		ret = self.interact([requests['REQ_GET_PWM_FRQ'],0,1,2])
		return ret[0] + ret[1]*256
	
	@freq1.setter
	def freq1(self, value):
		if value > 0:
			return self.interact([requests['REQ_SET_PWM_FRQ'],value,1,1])[0]
		else:
			return -1

	@property
	def freq2(self):
		#freq2 is the frequency for PWM 2
		ret = self.interact([requests['REQ_GET_PWM_FRQ'],0,2,2])
		return ret[0] + ret[1]*256
	
	@freq2.setter
	def freq2(self, value):
		if value > 0:
			return self.interact([requests['REQ_SET_PWM_FRQ'],value,2,1])[0]
		else:
			return -1

	@property
	def OD(self):
		ret = self.interact([requests['REQ_GET_PWM_DUTY'],0,0,2])
		return ret[0] + ret[1]*256
	
	@OD.setter
	def OD(self, value):
		if value > 0:
			return self.interact([requests['REQ_SET_PWM_DUTY'],value,0,1])[0]
		else:
			return -1

	@property
	def duty1(self):
		ret = self.interact([requests['REQ_GET_PWM_DUTY'],0,1,2])
		return ret[0] + ret[1]*256
	
	@duty1.setter
	def duty1(self, value):
		if value > 0:
			return self.interact([requests['REQ_SET_PWM_DUTY'],value,1,1])[0]
		else:
			return -1
	
	@property
	def duty2(self):
		ret = self.interact([requests['REQ_GET_PWM_DUTY'],0,2,2])
		return ret[0] + ret[1]*256
	
	@duty2.setter
	def duty2(self, value):
		if value > 0:
			return self.interact([requests['REQ_SET_PWM_DUTY'],value,2,1])[0]
		else:
			return -1