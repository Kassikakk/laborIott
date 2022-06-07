from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Newport1830.Inst import Newport1830 

pwrmtr = Newport1830.Newport1830(SDKAdapter("../Inst/usbdll", False))
print(pwrmtr.power)
pwrmtr.wl = 528
print(pwrmtr.wl)
