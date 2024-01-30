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
