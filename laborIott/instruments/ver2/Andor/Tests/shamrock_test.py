from laborIott.instruments.ver2.Andor.shamrock import Shamrock
from laborIott.adapters.ver2.SDKAdapter import SDKAdapter

shrock = Shamrock(SDKAdapter("ShamrockCIF", False), 26.0, 1024)

print(shrock.centerpos)
#print(shrock.wavelengths)
print(shrock.slit)
shrock.slit = 200
print(shrock.slit)
shrock.grating = 2
shrock.flipper = 'direct'
shrock.shutter = 'open'
print(shrock.flipper, shrock.shutter)
shrock.flipper = 'side'
shrock.shutter = 'closed'
print(shrock.flipper, shrock.shutter)
