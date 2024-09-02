'''
Ok so let's try to put together a simple procedure that only uses instruments as such, not VInsts
For example, let's calibrate the OD Ketas, thus only that and a powermeter is involved
We may later include TiSph, but first letäs use a lamp

'''

from laborIott.instruments.Inhouse.USBIO import USBIO
from laborIott.adapters.ver2.USBAdapter import USBAdapter
from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Newport1830.Inst import Newport1830  #should be converted to ver2

from time import sleep
import numpy as np
from math import log10

usbio = USBIO(USBAdapter(0xcacc, 0x0004))
pwrmtr = Newport1830.Newport1830(SDKAdapter("../Newport1830/Inst/usbdll", False)) #Miks ei leia System32st?

pwrmtr.wl = 400
usbio.freq1 = 300
usbio.OD = 1500



def measpwr():
	pow = []
	for i in range(20):
		pow.append(pwrmtr.power)
		sleep(0.05)
	return np.mean(pow)

ref = measpwr()

for duty in range(1500,8000,500):
	usbio.OD = duty
	sleep(1)
	sig = measpwr()
	print('{}	{}	{}'.format(duty, sig, log10(ref/sig)))

usbio.OD = 1500