from laborIott.instruments.ver2.OceanOptics.Flame import Flame
from laborIott.VInst.SpectroVI import Spectro_VI
from laborIott.adapters.ver2.SDKAdapter import SDKAdapter
from PyQt5 import QtWidgets
import sys

class Flame_VI(Spectro_VI):

	def __init__(self, refname="Flame"):
		super().__init__(refname)
		#connect or disable some controls
		self.elDarkChk.clicked.connect(self.setElDark)


	def connectInstr(self, refname):
		adapter = self.getZMQAdapter(refname)
		if adapter is None:
			adapter = SDKAdapter("OmniDriver32",False)
		self.instrum = Flame(adapter)

	def setElDark(self):
		self.instrum.corrElDark = 'on' if self.elDarkChk.isChecked() else 'off'
		
