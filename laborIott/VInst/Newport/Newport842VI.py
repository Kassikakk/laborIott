import sys
from PyQt5 import QtWidgets, QtGui


from laborIott.VInst.PowermVI import Powerm_VI

from laborIott.adapters.ver2.SerialAdapter import SerialAdapter
from laborIott.instruments.ver2.Newport.Newport842 import Newport842
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Newport842_VI(Powerm_VI):

	def __init__(self):
		#we might want to get the serial port data from the ini file here
		#NB about the timeout
		super().__init__('Nwp842', Newport842,SerialAdapter("COM5",baudrate=115200, timeout = 0.1))
		#self.setupUi(self)
		
		self.setWindowIcon(QtGui.QIcon(localPath('Newport.ico')))
		self.setWindowTitle("Newport 842")




if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	
	window = Newport842_VI()
	window.show()
	sys.exit(app.exec_())
