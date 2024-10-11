'''
Ok so let's try to put together a simple procedure that only uses instruments as such, not VInsts
For example, let's calibrate the OD Ketas, thus only that and a powermeter is involved
We may later include TiSph, but first letäs use a lamp

'''

from laborIott.instruments.Inhouse.USBIO import USBIO
from laborIott.adapters.ver2.USBAdapter import USBAdapter
#from laborIott.adapters.SDKAdapter import SDKAdapter
#from laborIott.instruments.Newport1830.Inst import Newport1830  
from laborIott.adapters.ver2.SDKAdapter import SDKAdapter
from laborIott.instruments.ver2.Newport.Newport1830 import Newport1830
import random

from time import sleep
import numpy as np
from math import log10

usbio = USBIO(USBAdapter(0xcacc, 0x0004))
pwrmtr = Newport1830(SDKAdapter("usbdll", False)) 
#pwrmtr = Newport1830.Newport1830(SDKAdapter("C:/Windows/System32/usbdll", False)) #Miks ei leia System32st?
#"../Newport1830/Inst/usbdll"
#"C:/Windows/System32/usbdll"

pwrmtr.wl = 900
usbio.freq1 = 300
usbio.duty0 = 1500



def measpwr():
	pow = []
	for i in range(20):
		pow.append(pwrmtr.power)
		sleep(0.2)
	return np.mean(pow)

ref = measpwr()

for duty in range(1500,7500,100):
#for i in range(20):
	#duty = random.randrange(1500,7500)
	#duty = [3000,4500,6000,4500][i%4]
	#usbio.duty0 = duty-200
	#sleep(1)
	usbio.duty0 = duty
	sleep(1)
	sig = measpwr()
	print('{}	{}'.format(duty, log10(ref/sig)))

usbio.duty0 = 1500