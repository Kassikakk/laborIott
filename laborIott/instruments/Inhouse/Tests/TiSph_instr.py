from laborIott.instruments.Inhouse.TiSph import TiSph
from laborIott.adapters.ver2.USBAdapter import USBAdapter
from time import sleep

tisph = TiSph(USBAdapter(0xcacc, 0x0002))
tisph.shutter = 'open'
sleep(1)
print(tisph.wavelength)
tisph.shutter = 'closed'
#tisph.disconnect()

