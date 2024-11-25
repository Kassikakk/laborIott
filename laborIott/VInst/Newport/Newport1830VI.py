import sys
from PyQt5 import QtWidgets, QtGui


from laborIott.VInst.PowermVI import Powerm_VI

from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Newport.Newport1830 import Newport1830
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Newport1830_VI(Powerm_VI):

	'''
	usbdll needed on path
	Now problem: reconnect gives error on  self.devID = int(devinfo[:devinfo.find(b',')])
	ValueError: invalid literal for int() with base 10: b"..."

	'''

	def __init__(self):
		
		#NB about the timeout
		super().__init__('Nwp1830', Newport1830,SDKAdapter("usbdll", False))
		#self.setupUi(self)
		
		self.setWindowIcon(QtGui.QIcon(localPath('Newport.ico')))
		self.setWindowTitle("Newport 1830")




if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	
	window = Newport1830_VI()
	window.show()
	sys.exit(app.exec_())
