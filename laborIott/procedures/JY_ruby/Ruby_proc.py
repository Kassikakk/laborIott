import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from threading import Thread, Event
from queue import Queue
from fittings.fittings import  fit_DLorentz, fit_DLorentz_slope
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
	updateData = QtCore.pyqtSignal(list)
	updateFitShape = QtCore.pyqtSignal(int, tuple, tuple, str)


	def __init__(self, address= None, inport= None, outport = None):
		super(RubyProc, self).__init__()
		self.setupUi(self) 

		self.andor = JYvon_VI(address, inport, outport)

		self.running = Event()
		self.processing = Event()
		self.processing.clear()
		self.runThread = None
		self.paramlist = None
		'''
		#self.plot = self.graphicsView.plot([0, 1], [0, 0], pen=(255, 131, 0))  # fanta
		self.plotx = [[0, 1]]
		self.ploty = [[0, 0]]
		self.spectraX = self.andor.getX()  # get the current x scale
		'''
		self.closeEvent = lambda a: self.andor.hide()
		self.startIdus.connect(self.andor.run)

		self.setExternalMode.connect(self.andor.setExternal)
		self.updateFitShape.connect(self.andor.setOverlay)
		self.updateData.connect(self.update)
		self.runButt.clicked.connect(self.onStart)
		# also connect all changes to paramqueue set

		self.andor.show()

		
	
	

	def update(self, spcData):
		xData = self.andor.xarr

		if self.paramlist is not None and self.cyclicCheck.isChecked():  # go cyclic if possible
			delim = (self.paramlist[0] + self.paramlist[3]) / 2
		else:
			self.paramlist = None
			delim = None  # võetakse skaala keskpunkt

		if self.slopeCheck.isChecked():
			if self.paramlist is not None and len(self.paramlist) == 7:
				self.paramlist += [0.0]
			fitted, params = fit_DLorentz_slope(np.array(spcData), xData, delim,
												self.paramlist)  # eraldusx maksimumide vahel
			self.paramlist = [params[0][i * 2] for i in range(8)]
		else:
			if self.paramlist is not None and len(self.paramlist) == 8:
				self.paramlist = self.paramlist[:7]
			fitted, params = fit_DLorentz(np.array(spcData), xData, delim, self.paramlist)
			self.paramlist = [params[0][i * 2] for i in range(7)]
		self.updateFitShape.emit(0, tuple(xData), tuple(fitted[0]), 'w')

		p = (params[0][6] - float(self.zeroValEdit.text())) / float(self.coefEdit.text())
		# self.pLabel.setText("{:.2f}".format(p))
		self.pLabel.setText("{:.2f}".format(params[0][6]))
		self.RLabel.setText("{:.4f}".format(params[0][7]))
		self.SNLabel.setText("{:.1f}".format(params[0][-1]))
		self.processing.clear()

		'''
		p = (params[6] - float(self.zeroValEdit.text()))/float(self.coefEdit.text())
		self.pLabel.setText("{:.2f}".format(p))
		self.pLabel.setText("{:.2f}".format(params[6]))
		self.RLabel.setText("{:.4f}".format(params[7]))
		self.SNLabel.setText("{:.1f}".format(params[-1]))
		'''

	def onStart(self):
		if self.running.is_set():
			# end running
			self.running.clear()
			self.runThread.join()
			self.setExternalMode.emit(False)
		else:
			self.runThread = Thread(target=self.runProc) #args passed by queue
			self.setExternalMode.emit(True)
			self.running.set()
			self.runThread.start()

	def runProc(self):
		spcData = None
		while (True):
			# get andor spectral data
			self.startIdus.emit(True)
			# process previous data while acquiring
			if spcData is not None:
				self.processing.set()
				self.updateData.emit(spcData)
			# wait for data arrival
			while self.andor.dataQ.empty() or self.processing.is_set():
				if not self.running.is_set():
					return
			spcData = self.andor.dataQ.get(False)
			# check once more
			if not self.running.is_set():
				return

		'''#-------------------------------
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
				fitted, params = fit_DLorentz(np.array(spcData), xData, delim, paramlist)
				paramlist = [params[0][i * 2] for i in range(7)]
			# TODO: decide somehow if the line is meaningful, otherwise no point in doing the next part
			self.updateData.emit(tuple(params[0]))
			self.updateFitShape.emit(0, tuple(xData), tuple(fitted[0]), 'w')
			'''


def ExitHandler():
	#QtWidgets.QMessageBox.information(None,window.wlLabel.text() , "Going somewhere?")
	#anything needed before checkout
	pass




if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	app.aboutToQuit.connect(ExitHandler)
	# handle possible command line parameters: address, inport, outport
	args = sys.argv[1:4]
	# port values, if provided, should be integers
	# this errors if they are not
	for i in (1,2):
		if len(args) > i:
			args[i] = int(args[i])
	window = RubyProc(*args)
	window.show()
	sys.exit(app.exec_())