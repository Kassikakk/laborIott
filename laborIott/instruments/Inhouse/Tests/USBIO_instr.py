from laborIott.instruments.Inhouse.USBIO import USBIO
from laborIott.adapters.USBAdapter import USBAdapter
from time import sleep

usbio = USBIO(USBAdapter(0xcacc, 0x0004))

usbio.freq2 = 50
usbio.duty2 = 3000
sleep(1)
usbio.duty2 = 1000
'''
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

usbio.freq1 = 300
usbio.OD = 2000
'''
print(usbio.freq1)
usbio.freq1 = 0
sleep(2)


print(usbio.freq1)
usbio.setpin(1,1)
