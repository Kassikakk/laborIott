from laborIott.instruments.ver2.Andor.andor import IDus
from laborIott.VInst.SpectroVI import Spectro_VI
from laborIott.adapters.ver2.SDKAdapter import SDKAdapter
from PyQt5 import QtWidgets
import sys

class iDus_VI(Spectro_VI):

	def __init__(self, refname="iDus"):
		super().__init__(refname)


	def connectInstr(self, refname):
		adapter = self.getZMQAdapter(refname)
		if adapter is None:
			adapter = SDKAdapter("atmcd32d_legacy",False)
		self.instrum = IDus(adapter)








if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
		
	window = iDus_VI() #you may add a different refname as a parameter
	window.show()
	sys.exit(app.exec_())