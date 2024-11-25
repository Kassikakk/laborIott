import sys
from PyQt5 import QtWidgets, QtGui


from laborIott.VInst.PowermVI import Powerm_VI

from laborIott.adapters.SerialAdapter import SerialAdapter
from laborIott.instruments.Newport.Newport842 import Newport842
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Newport842_VI(Powerm_VI):

	def __init__(self):
		#we might want to get the serial port data from the ini file here
		#NB about the timeout
		super().__init__('Nwp842', Newport842,SerialAdapter("/dev/ttyUSB0",baudrate=115200, timeout = 0.1))
		#It appears that Newport 842 can do about 4 measurements per second, so if polled at 0.2 sec intervals,
		#about every 4th query will timeout, or, if timeout value is increased, timer cycles will be skipped

		#Also note that attenuator here is not updated automatically in the device (unlike Newport 1830), so no point
		#to include querying it in the timer routine
		#However, switching to autoscale actually should work?

		
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
