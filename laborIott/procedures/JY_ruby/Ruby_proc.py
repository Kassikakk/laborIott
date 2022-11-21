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

		self.values = [[],[]]
		self.colsum = [0,0]
		self.colsum2 = [0,0]
		self.collecting = False
		self.saveLoc = './'
		self.running = Event()
		self.processing = Event()
		self.processing.clear()
		self.settings_queue = Queue()
		self.runThread = FitWorker(self.startIdus, self.andor.dataQ, self.settings_queue)
		self.colorlist = ['w', 'r'] #fitted overlay colors
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
		self.fitBox1.toggled.connect(lambda a:  self.setSettingsQueue('active'))
		self.fitBox2.toggled.connect(lambda a: self.setSettingsQueue('active'))
		self.rangeSetButt1.clicked.connect(lambda a: self.setSettingsQueue('range'))
		self.rangeSetButt2.clicked.connect(lambda a: self.setSettingsQueue('range'))
		self.slopeChk1.toggled.connect(lambda a: self.setSettingsQueue('sloped'))
		self.slopeChk2.toggled.connect(lambda a: self.setSettingsQueue('sloped'))
		self.cyclicChk1.toggled.connect(lambda a: self.setSettingsQueue('cyclic'))
		self.cyclicChk2.toggled.connect(lambda a: self.setSettingsQueue('cyclic'))
		self.relRangeChk1.toggled.connect(lambda a: self.setSettingsQueue('relrange'))
		self.relRangeChk2.toggled.connect(lambda a: self.setSettingsQueue('relrange'))
		self.modelCombo1.currentIndexChanged.connect(lambda a: self.setSettingsQueue('model'))
		self.modelCombo2.currentIndexChanged.connect(lambda a: self.setSettingsQueue('model'))
		self.showPRadio1.toggled.connect(lambda a: self.pUnitLabel1.setText('kbar' if self.showPRadio1.isChecked() else 'nm'))
		self.showPRadio2.toggled.connect(lambda a: self.pUnitLabel2.setText('kbar' if self.showPRadio2.isChecked() else 'nm'))

		self.setZeroFromT1.clicked.connect(lambda a: self.calcZeroWl(0))

		self.startButt.clicked.connect(lambda: self.setCollect(not self.collecting))
		self.resetButt.clicked.connect(self.resetSeries)
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda: self.saveData(self.nameEdit.text()))

		self.andor.show()

		
	def setSettingsQueue(self, setting = None): #handle the params queue
		#if there is a dict in the queue already, grab it first
		#Then the queue should be empty
		p_dict = {} if self.settings_queue.empty() else self.settings_queue.get(False)
		#['active', 'range', 'sloped','cyclic', 'model']
		if setting is None or setting == 'active':
			clist = [self.fitBox1.isChecked(),self.fitBox2.isChecked()]
			p_dict['active'] = clist
			#also remove deactivated curves
			for i,n  in enumerate(clist):
				if not n:
					self.andor.setOverlay(i, [],[],None)
			
		if setting is None or setting == 'range' or setting == 'relrange':
			try:
				#this requires a rather strict validation since during editing all kinds of values may appear transiently
				#convert from 1 - to 0 - based list
				trylist = [[int(self.rangeLowEdit1.text()) - 1, int(self.rangeHighEdit1.text()) - 1], [int(self.rangeLowEdit2.text()) - 1, int(self.rangeHighEdit2.text()) - 1]]
				listok = True
				for i in range(2):
					if trylist[i][0] < 0 or trylist[i][1] > 1023 or trylist[i][0] > trylist[i][1]:
						listok = False 
				if listok:
					p_dict['range'] = trylist
				if setting == 'relrange':
					p_dict['relrange'] = [self.relRangeChk1.isChecked(), self.relRangeChk2.isChecked()]
			except ValueError: #just forget it
				pass
			#TODO: try and range check should be performed here
		if setting is None or setting == 'sloped':
			p_dict['sloped'] = [self.slopeChk1.isChecked(), self.slopeChk2.isChecked()]
		if setting is None or setting == 'cyclic':
			p_dict['cyclic'] = [self.cyclicChk1.isChecked(), self.cyclicChk2.isChecked()]
		if setting is None or setting == 'model':
			p_dict['model'] = [self.modelCombo1.currentText(), self.modelCombo2.currentText()] #or was it getText?
		self.settings_queue.put(p_dict)



	

	def update(self, dataTuple):

		if dataTuple[1] is None: # rejected result
			return #we could add some sign here, e.g. make some text red

		index, paramlist, xData, fitted, uncertlist, chi = dataTuple #we can add more here as reqd
		self.updateFitShape.emit(index, tuple(xData), tuple(fitted), self.colorlist[index])
		pRadio, pLabel, RLabel, SNLabel, zeroValEdit, NLabel, meanLabel, stdevLabel = \
			(
			self.showPRadio1, self.pLabel1, self.RLabel1, self.SNLabel1, self.zeroValEdit1,
			self.NLabel1, self.meanLabel1, self.stdevLabel1
		) if index == 0 else (
			self.showPRadio2, self.pLabel2, self.RLabel2, self.SNLabel2, self.zeroValEdit2,
			self.NLabel2, self.meanLabel2, self.stdevLabel2)

		if pRadio.isChecked(): #show pressure
			p = (paramlist[0] - float(zeroValEdit.text())) / float(self.coefEdit.text())
			pLabel.setText("{:.3f}".format(p))
		else: #show wavelength
			pLabel.setText("{:.3f}".format(paramlist[0]))

		RLabel.setText("{:.4f}".format(chi))
		SNLabel.setText("{:.3f}".format(uncertlist[0]))
		if self.collecting:
			colval = p if pRadio.isChecked() else paramlist[0]
			self.values[index].append([int(time()*10 - 16e9), colval])  # collect power while acquiring
			self.colsum[index] += colval
			self.colsum2[index] += colval**2
			N = len(self.values[index])
			mean = self.colsum[index] / N
			var = np.sqrt(self.colsum2[index] / N  - mean**2)
			# update mean and stdev vals
			NLabel.setText("{}".format(N))
			meanLabel.setText("{}".format(mean))  # mida siia?
			stdevLabel.setText('%s' % float('%.2g' % var))



	def onStart(self):
		if self.runThread.running.is_set():
			# end running
			self.runThread.stop()
			#self.runThread.join() #looks like QThread doesnät have it
			#remove fitting curves
			for i in range(2):
				self.andor.setOverlay(i, [],[],None)
			self.setExternalMode.emit(False)
		else:
			#load up settings queue
			self.setSettingsQueue() #load up all params
			self.setExternalMode.emit(True)
			self.runThread.start()


	def calcZeroWl(self, fitter):

		zWL, dzWL =[[self.zeroValEdit1,self.dZeroValEdit1],[self.zeroValEdit2,self.dZeroValEdit2]][fitter]
		try:
			T = float(self.tempEdit.text())
			dT = float(self.deltaTempEdit.text())
		except ValueError:
			return
		#Let's believe Syassen values of the coefficients (for R1)
		alphav = 76.6
		dalphav = 6.9
		theta = 482
		dtheta = 20
		nv0 = 14421.8
		dnv0 = 0.4

		#It shouldn't be too hard to calculate the wavelength now
		expval = np.exp(theta / T) - 1

		lambda0 = 1e7*expval / (nv0 * expval - alphav)

		#now the uncert consists of 4 parts:
		errbase = lambda0 / (nv0 * expval - alphav)
		#due to alphav:
		d1 = errbase * dalphav
		#due to theta and T:
		#common = 1e7 * alphav * (expval + 1) / ((nv0 * expval - alphav)**2)
		# should be == errbase * alphav * (1 + 1/expval)
		d2 = errbase * alphav * (1 + 1/expval) * dtheta / T
		d3 = errbase * alphav * (1 + 1/expval) * theta * dT / (T**2)
		# due to nv0
		d4 = errbase * expval * dnv0
		#combined uncert
		dlambda0 = np.sqrt(d1**2 + d2**2 + d3**2 + d4**2)
		print(d1, d2, d3, d4, dlambda0)
		zWL.setText("{:.4f}".format(lambda0))
		dzWL.setText("{:.4f}".format(dlambda0))

	def setCollect(self, value, clearOnStart=False):

		if (value and clearOnStart):
			self.values = [[], []]
			self.colsum = [0, 0]
			self.colsum2 = [0, 0]
		self.startButt.setText("Pause" if value else "Cont")
		self.collecting = value

	def resetSeries(self):
		if not self.collecting:
			self.startButt.setText("Start")
		self.values = [[], []]
		self.colsum = [0, 0]
		self.colsum2 = [0, 0]



	# saving

	def onGetLoc(self):
		self.saveLoc = QtWidgets.QFileDialog.getExistingDirectory(self, "Save location:", "./",
																  QtWidgets.QFileDialog.ShowDirsOnly
																  | QtWidgets.QFileDialog.DontResolveSymlinks)
		self.locLabel.setText(self.saveLoc)

	def saveData(self, name):
		# saves existing data under self.saveLoc + name
		# however, name validity and existance should be checked first
		# also if we have any data
		if len(name) == 0:
			return
		index = 0 if self.saveRadio1.isChecked() else 1
		if len(self.values[index]) == 0:
			return

		if self.formatCombo.currentText() == 'ASCII XY':
			data = pd.DataFrame(list(self.values[index]))
			# if zip, support it here
			data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False)
			# the rest will follow
		elif self.formatCombo.currentText() == 'ASCII Y':
			data = pd.DataFrame([self.values[index][i][1] for i in range(len(self.values[index]))])
			# if zip, support it here
			data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False)
			# the rest will follow





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