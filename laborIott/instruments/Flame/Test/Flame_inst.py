from adapters.SDKAdapter import SDKAdapter
from Flame.Inst import Flame #instruments folder on pathi peal

flame = Flame.Flame(SDKAdapter("../OmniDriver32", False))

flame.expTime = 1
flame.status = 'start'
while len(flame.asyncready) == 0:
	pass
print(getattr(flame,flame.asyncready[0]))
