import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from threading import Thread, Event
from queue import Queue
from fitworker import FitWorker
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
		self.settings_queue = Queue()
		self.runThread = FitWorker(self.startIdus, self.andor.dataQ, self.param_queue)
		self.colorlist = ['w', 'b'] #fitted overlay colors
		'''
		#self.plot = self.graphicsView.plot([0, 1], [0, 0], pen=(255, 131, 0))  # fanta
		self.plotx = [[0, 1]]
		self.ploty = [[0, 0]]
		self.spectraX = self.andor.getX()  # get the current x scale
		'''
		self.closeEvent = lambda a: self.andor.hide()
		self.startIdus.connect(self.andor.run)
		self.runThread.dataReady.connect(self.update)

		self.setExternalMode.connect(self.andor.setExternal)
		self.updateFitShape.connect(self.andor.setOverlay)
		self.updateData.connect(self.update)
		self.runButt.clicked.connect(self.onStart)
		# also connect all changes to settingsqueue set
		self.fitBox1.changed.connect(lambda a:  self.setSettingsQueue('active'))
		self.fitBox2.changed.connect(lambda a: self.setSettingsQueue('active'))
		self.rangeLowEdit1.changed.connect(lambda a: self.setSettingsQueue('range'))
		self.rangeHighEdit1.changed.connect(lambda a: self.setSettingsQueue('range'))
		self.rangeLowEdit2.changed.connect(lambda a: self.setSettingsQueue('range'))
		self.rangeHighEdit2.changed.connect(lambda a: self.setSettingsQueue('range'))
		self.slopeChk1.changed.connect(lambda a: self.setSettingsQueue('sloped'))
		self.slopeChk2.changed.connect(lambda a: self.setSettingsQueue('sloped'))
		self.cyclicChk1.changed.connect(lambda a: self.setSettingsQueue('cyclic'))
		self.cyclicChk2.changed.connect(lambda a: self.setSettingsQueue('cyclic'))
		self.modelCombo1.changed.connect(lambda a: self.setSettingsQueue('model'))
		self.modelCombe2.changed.connect(lambda a: self.setSettingsQueue('model'))
		self.showPRadio1.changed.connect(lambda a: self.pUnitLabel1.setText('kbar' if self.showPRadio1.isChecked() else 'nm'))
		self.showPRadio2.changed.connect(lambda a: self.pUnitLabel2.setText('kbar' if self.showPRadio2.isChecked() else 'nm'))

		self.andor.show()

		
	def setSettingsQueue(self, setting = None): #handle the params queue
		#if there is a dict in the queue already, grab it first
		#Then the queue should be empty
		p_dict = {} if self.settings_queue.empty() else self.settings_queue.get(False)
		#['active', 'range', 'sloped','cyclic', 'model']
		if setting is None or setting == 'active':
			p_dict['active'] = [self.fitBox1.isChecked(),self.fitBox2.isChecked()]
		if setting is None or setting == 'range':
			p_dict['range'] = [[int(self.rangeLowEdit1.text()), int(self.rangeHighEdit1.text())], [int(self.rangeLowEdit2.text()), int(self.rangeHighEdit2.text())]]
			#TODO: try and range check should be performed here
		if setting is None or setting == 'sloped':
			p_dict['sloped'] = [self.slopeChk1.isChecked(), self.slopeChk2.isChecked()]
		if setting is None or setting == 'cyclic':
			p_dict['cyclic'] = [self.cyclicChk1.isChecked(), self.cyclicChk2.isChecked()]
		if setting is None or setting == 'model':
			p_dict['model'] = [self.modelCombo1.text(), self.modelCombo2.text()] #or was it getText?
		self.settings_queue.put(p_dict)



	

	def update(self, dataTuple):

		if dataTuple[1] is None: # rejected result
			return #we could add some sign here, e.g. make some text red

		index, paramlist, xData, fitted, uncertlist, chi = dataTuple #we can add more here as reqd
		self.updateFitShape.emit(index, tuple(xData), tuple(fitted), self.colorlist[index])
		pRadio, plabel, RLabel, SNLabel = (self.showPRadio1,
										   self.pLabel1, self.RLabel1, self.SNLabel1) if index == 0 else (self.showPRadio2,
																										  self.pLabel2, self.RLabel2, self.SNLabel2)

		if pRadio.isChecked(): #show pressure
			p = (paramlist[0] - float(self.zeroValEdit.text())) / float(self.coefEdit.text())
			pLabel.setText("{:.2f}".format(p))
		else: #show wavelength
			pLabel.setText("{:.2f}".format(paramlist[0]))

		RLabel.setText("{:.4f}".format(chi))
		SNLabel.setText("{:.1f}".format(uncertlist[0]))


	def onStart(self):
		if self.runThread.running.is_set():
			# end running
			self.runThread.stop()
			self.runThread.join()
			self.setExternalMode.emit(False)
		else:
			#load up settings queue
			self.setSettingsQueue() #load up all params
			self.setExternalMode.emit(True)
			self.runThread.start()






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