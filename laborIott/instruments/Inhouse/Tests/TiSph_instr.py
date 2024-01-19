from laborIott.instruments.Inhouse.TiSph import TiSph
from laborIott.adapters.ver2.USBAdapter import USBAdapter
from time import sleep

tisph = TiSph(USBAdapter(0xcacc, 0x0002))
print(tisph.wavelength)
tisph.shutter = 'open'
sleep(1)
tisph.speed = 150
tisph.wavelength = 760
#print(tisph.wavelength)
tisph.shutter = 'closed'
#tisph.disconnect()
#730-744.4 = 767 steps

