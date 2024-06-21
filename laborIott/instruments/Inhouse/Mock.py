from laborIott.instruments.instrument import Instrument


class Mock(Instrument):

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "Mock", **kwargs)
		self._maxlim = 100

	
	@property
	def rndval(self):
		if self.connected:
			return self.interact([1,0,self._maxlim])

	@rndval.setter
	def rndval(self, value):
		self._maxlim = value