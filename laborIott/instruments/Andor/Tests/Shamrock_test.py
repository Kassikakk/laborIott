import os
from time import sleep
from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Andor.Inst.shamrock import Shamrock

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

shrock = Shamrock(SDKAdapter(localPath("../Inst/ShamrockCIF"), False), 26.0, 1024)


#print(shrock.centerpos)
#print(shrock.wavelengths)
#print(shrock.slit)
#shrock.slit = 100
#print(shrock.slit)
#shrock.grating = 2
shrock.flipper = 'direct'
shrock.shutter = 'open'
print(shrock.flipper, shrock.shutter)
shrock.flipper = 'side'
shrock.shutter = 'closed'
print(shrock.flipper, shrock.shutter)