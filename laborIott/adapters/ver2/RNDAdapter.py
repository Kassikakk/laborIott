from laborIott.adapters.adapter import Adapter

from random import randrange


class RNDAdapter(Adapter):

	def __init__(self):
		super().__init__()

	def interact(self,valrng):
		if valrng[0] == 0: #echo back
			return [valrng[1]]
		elif valrng[0] == 1:
			return [randrange(*(valrng[1:]))]
		else:
			return []