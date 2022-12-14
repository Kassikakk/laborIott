from laborIott.instrument import Instrument


class Shamrock(Instrument):

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "Shamrock", **kwargs)
		self.write("ShamrockInitialize('')")