from laborIott.instrument import Instrument


class Shamrock(Instrument):

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "Shamrock", **kwargs)
		self.write("ShamrockInitialize('')")


	#wavelengths
	#centerpos NB 0 supported
	#slit
	#grating
	#gratingdict