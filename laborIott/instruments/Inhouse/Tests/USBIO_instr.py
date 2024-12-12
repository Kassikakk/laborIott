from laborIott.instruments.Inhouse.USBIO import USBIO
from laborIott.adapters.USBAdapter import USBAdapter
from time import sleep

usbio = USBIO(USBAdapter(0xcacc, 0x0004))
'''
usbio.freq2 = 100
usbio.duty2 = 3000
sleep(1)
usbio.duty2 = 700
usbio.freq2 = 0

usbio.freq1 = 100
usbio.duty1 = 2400
sleep(1)
usbio.duty1 = 700
sleep(1)
usbio.duty1 = 1000
sleep(1)
usbio.duty1 = 2000
#usbio.freq2 = 0
'''
usbio.freq1 = 300
usbio.OD = 2000

sleep(2)
print(usbio.freq1)
usbio.freq1 = 0

usbio.setpin(1,1)
