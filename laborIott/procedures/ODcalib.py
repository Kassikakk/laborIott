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
pwrmtr = Newport1830.Newport1830(SDKAdapter("../Inst/usbdll", False))

usbio.freq1 = 300
usbio.duty1 = 1500

ref = measpwr()

def measpwr():
	pow = []
	for i in range(20):
		pow.append(pwrmtr.power)
		sleep(0.05)
	return np.mean(pow)


for duty in range(1500,8000,500):
	usbio.duty1 = duty
	sleep(1)
	sig = measpwr()
	print('{}	{}	{}'.format(duty, sig, log10(sig/ref)))

