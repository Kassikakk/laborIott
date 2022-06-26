import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from threading import Thread, Event
from time import sleep, strftime, time
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd


from laborIott.instruments.Andor.VInst.JYvon_VI import JYvon_VI


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class RubyProc(*uic.loadUiType(localPath('RubyPressure.ui'))):
	
	setpowerWL = QtCore.pyqtSignal(float)

	def __init__(self):
		super(RubyProc, self).__init__()
		self.setupUi(self) 

		self.andor = JYvon_VI()

		self.startIdus.connect(self.andor.run)

		self.setExternalMode.connect(self.andor.setExternal)

		self.andor.show()

	def onStart(self):
		if self.scanning.isSet():
			# end scanning
			self.cleanScan()
			self.scanThread.join()

		else:



if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	window = RubyProc()
	window.show()
	sys.exit(app.exec_())