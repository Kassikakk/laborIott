from laborIott.instruments.ver2.Andor.andor import IDus
from laborIott.adapters.ver2.SDKAdapter import SDKAdapter

idus = IDus(SDKAdapter("atmcd32d_legacy", False))

print(idus.temperature)