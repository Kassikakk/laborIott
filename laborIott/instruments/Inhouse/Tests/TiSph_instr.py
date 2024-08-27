from laborIott.instruments.Inhouse.TiSph import TiSph
from laborIott.adapters.ver2.USBAdapter import USBAdapter
from laborIott.adapters.ver2.ZMQAdapter import ZMQAdapter
from time import sleep

tisph = TiSph(USBAdapter(0xcacc, 0x0002))
#tisph = TiSph(ZMQAdapter('jobinyvon', 5555))
print(tisph.wavelength)
tisph.shutter = 'open'
sleep(1)
'''
tisph.speed = 50
tisph.wavelength = 865.62
while tisph.status == 'moving':
	print(tisph.wavelength)
	sleep(0.5)
'''
tisph.shutter = 'closed'
tisph.status = 'release'
#700 nm on piir praegu - 940
#tisph.disconnect()
#730-744.4 = 767 steps

