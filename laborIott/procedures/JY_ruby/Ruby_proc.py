import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from threading import Thread, Event
from queue import Queue
from fittings import  fit_DLorentz, fit_DLorentz_slope
from time import sleep, strftime, time
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd


from laborIott.instruments.Andor.VInst.JYvon_VI import JYvon_VI


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class RubyProc(*uic.loadUiType(localPath('RubyPressure.ui'))):
	
	setExternalMode = QtCore.pyqtSignal(bool)
	startIdus = QtCore.pyqtSignal(bool)
	updateData = QtCore.pyqtSignal(tuple)
	updateFitShape = QtCore.pyqtSignal(tuple)


	def __init__(self):
		super(RubyProc, self).__init__()
		self.setupUi(self) 

		self.andor = JYvon_VI()

		self.running = Event()
		self.runThread = None
		self.paramQueue = Queue()
		'''
		#self.plot = self.graphicsView.plot([0, 1], [0, 0], pen=(255, 131, 0))  # fanta
		self.plotx = [[0, 1]]
		self.ploty = [[0, 0]]
		self.spectraX = self.andor.getX()  # get the current x scale
		'''

		self.startIdus.connect(self.andor.run)
		self.setExternalMode.connect(self.andor.setExternal)
		self.runButt.clicked.connect(self.onStart)
		# also connect all changes to paramqueue set

		self.andor.show()

	def loadQueue(self):
		# load parameters to paramQueue to pass to thread
		# match it with thread params: add more params if needed
		paramtuple = (self.slopeCheck.isChecked(), self.cyclicCheck.isChecked() )
		# make sure the queue is empty
		while not self.paramQueue.empty():
			self.paramQueue.get(False)
		self.paramQueue.put(paramtuple)

	def onStart(self):
		if self.running.is_set():
			# end running
			self.running.clear()
			self.runThread.join()
			self.setExternalMode.emit(False)
		else:
			self.runThread = Thread(target=self.runProc) #args passed by queue
			self.setExternalMode.emit(True)
			self.loadQueue()
			self.running.set()
			self.runThread.start()

	def runProc(self):
		paramlist = None
		delim = None
		sloped, cyclic = True, True
		while(True):
			#get andor x data
			xData = self.andor.xarr # is this dangerous?
			#get andor spectral data
			self.startIdus.emit(True)  # reserve false for abort?
			# wait for data arrival
			while self.andor.dataQ.empty():
				if not self.running.is_set():
					return
			spcData = self.andor.dataQ.get(False)
			#check param queue & set params
			if not self.paramQueue.empty():
				sloped, cyclic = self.paramQueue.get(False)
			# do the fitting(s)
			# can this be put to a separate fn?
			if paramlist is not None and cyclic:  # go cyclic if possible
				delim = (paramlist[0] + paramlist[3]) / 2
			else:
				paramlist = None
				delim = None  # võetakse skaala keskpunkt

			if sloped:
				if paramlist is not None and len(paramlist) == 7:
					paramlist += [0.0]
				fitted, params = fit_DLorentz_slope(np.array(spcData), xData, delim,
													paramlist)  # eraldusx maksimumide vahel
				paramlist = [params[0][i * 2] for i in range(8)]
			else:
				if paramlist is not None and len(paramlist) == 8:
					paramlist = paramlist[:7]
				fitted, params = fit_DLorentz(np.array(self.data), self.xarr, delim, paramlist)
				paramlist = [params[0][i * 2] for i in range(7)]
			self.updateData.emit(tuple(params[0]))
			self.updateFitShape.emit(tuple(fitted[0]))

			#emit the numerical results to main thread
			#emit the fitted spectrum to andor
			#check if running is still set, else break
			#that should be it





if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	window = RubyProc()
	window.show()
	sys.exit(app.exec_())