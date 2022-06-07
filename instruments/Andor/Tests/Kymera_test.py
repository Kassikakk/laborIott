import os
from time import sleep
from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Andor.Inst.kymera import IDusKymera

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

kymera = IDusKymera(SDKAdapter(localPath("../Inst/atmcd32d_legacy"), False))

		
#kymera.centerpos = 800
kymera.focus = 30
print(kymera.focus)
#print(kymera.centerpos)
#print(kymera.filterdict)
#print(kymera.gratingdict)


