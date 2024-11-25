from laborIott.instruments.Andor.andor import IDus
from laborIott.adapters.SDKAdapter import SDKAdapter

idus = IDus(SDKAdapter("atmcd32d_legacy", False))

print(idus.temperature)
