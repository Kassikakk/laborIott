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

