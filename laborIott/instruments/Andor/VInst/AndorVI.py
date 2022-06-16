import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pyqtgraph as pg
import pandas as pd

from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.adapters.ZMQAdapter import ZMQAdapter
from laborIott.instruments.Andor.Inst.andor import IDus 
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

from queue import Queue
#from threading import Thread, Event
#from time import sleep, strftime, time
#import numpy as np
from math import log10

#import Spectra


#Ui_MainWindow, QMainWindow = uic.loadUiType(localPath('Andor.ui'))

class Andor_VI(*uic.loadUiType(localPath('Andor.ui'))):

	def __init__(self, address= None, inport= None, outport = None):
		super(Andor_VI, self).__init__()
		self.setupUi(self)

		#connect instrument
		self.connectInstr(address, inport, outport)
		
		#parameetrid
		self.data = []
		self.back = []
		self.ref = []
		self.idus.noAccum = 1
		self.idus.expTime = 0.5
		self.idus.acqmode = 'single'
		self.acquiring = False
		self.saveLoc = './'
		self.external = False
		self.dataQ = Queue()
		self.dsbl = [self.runButt, self.setParmsButt, self.backChk, self.locButt, self.saveButt, self.formatCombo]
		
		#plot
		self.xarr = self.idus.wavelengths

		#self.graphicsView.setBackground('w')
		self.plot = self.graphicsView.plot([self.xarr[0],self.xarr[-1]],[0,1], pen = (255,131,0)) #fanta

		
		
		#connect section
		self.runButt.clicked.connect(self.run)
		self.coolButt.clicked.connect(self.cooler) #implement
		self.shutButt.clicked.connect(self.setShutter)
		self.setParmsButt.clicked.connect(self.onSetParms) 
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda : self.saveData(self.nameEdit.text()))

		
		#konnektid
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)
		

	def connectInstr(self, address, inport, outport):
		#instrumendi tekitamine
		if address is None:
			# local instrument
			self.idus = IDus(SDKAdapter(localPath("../Inst/atmcd32d_legacy"), False))
		else:
			# connect to remote instrument
			# default port is 5555
			inp = 5555 if inport is None else inport
			outp = inp if outport is None else outport
			self.idus = IDus(ZMQAdapter("iDus", address, inp, outp))

		
		
		
	def onTimer(self):
		
		if self.acquiring and self.idus.status != 'Acqring': #measurement data arrival 
			datalist = self.idus.data
			#datalist.reverse() #if needed
			self.setAcq(False)
			
			#back set või lahut.
			if self.backChk.isChecked():
				self.back = datalist
				self.sigChk.setChecked(True)
				self.runButt.setChecked(False)
				if len(self.back) == len(self.ref):
					self.absChk.setEnabled(True)
				self.plot.setData(self.xarr,datalist)
				
			elif self.refChk.isChecked():
				self.ref = datalist
				self.sigChk.setChecked(True)
				self.runButt.setChecked(False)
				if len(self.back) == len(self.ref):
					self.absChk.setEnabled(True)
					datalist = [self.ref[i] - self.back[i] for i in range(len(self.back))]
				self.plot.setData(self.xarr,datalist)
			else:
				if len(self.back) == len(datalist):
					if not self.absChk.isChecked():
						self.data = [datalist[i] - self.back[i] for i in range(len(datalist))]
					else:
						#calculate absorption
						self.data = []
						for i in range(len(datalist)):
							R = (self.ref[i] - self.back[i])
							S = (datalist[i] - self.back[i])
							if R > 0 and S > 0:
								self.data += [log10(R) - log10(S)]
							else:
								self.data += [0]

				else:
					self.data = datalist
				self.plot.setData(self.xarr,self.data)
				if self.external:
					self.dataQ.put(self.data)
			

			
			if self.runButt.isChecked():
				self.idus.status = 'start'
				#print("Sending start again")
				self.setAcq(True)
				
		#display the temperature & status
		temp = self.idus.temperature
		if(temp[1]): #if not acquiring
			self.tempLabel.setText("{}°C / {}".format(temp[1], temp[0]))
				
	def setAcq(self, state):
		self.acquiring = state
		for wdg in [self.setParmsButt, self.saveButt]:
			wdg.setEnabled(not state)


	def run(self):
		if (self.acquiring): #ongoing acquisition
			return
		if self.runButt.isChecked() or self.external:
			#start running
			self.idus.status = 'start'
			#print("Sending start")
			self.setAcq(True)
			
	def setExpTime(self, value):
		if (self.acquiring): #ongoing acquisition
			return
		try:
			exp = float(value)
			#range
			if (exp <= 0): 
				self.expEdit.setText("#low")
				return
			self.idus.expTime = exp
			self.expEdit.setText("%.3f" % self.idus.expTime)
		except ValueError:
			self.expEdit.setText("#err")
			
	def setNoAccum(self, value):
		if (self.acquiring): #ongoing acquisition
			return
		try:
			noAcc = int(value)
			#range
			if (noAcc < 0): 
				self.noAccEdit.setText("#low")
				return
			self.idus.noAccum = noAcc
			self.idus.acqmode = 'single' if (noAcc < 2) else 'accum'
			self.noAccEdit.setText(str(self.idus.noAccum))
		except ValueError:
			self.noAccEdit.setText("#err")
			
	def onSetParms(self):
		self.setExpTime(self.expEdit.text())
		self.setNoAccum(self.noAccEdit.text())

			
	def cooler(self):
		if (self.coolButt.isChecked()):
			try:
				temp = int(self.tempEdit.text())
			except ValueError:
				self.tempEdit.setText("#err")
				self.coolButt.setChecked(False)
				return 
			self.idus.temperature = temp
		else:
			self.idus.temperature =  None
	
	def setShutter(self):
		self.idus.shutter = 'open' if self.shutButt.isChecked() else 'closed'
	
	def getX(self):
		return self.xarr
			
	def onGetLoc(self):
		self.saveLoc = QtWidgets.QFileDialog.getExistingDirectory(self, "Save location:", "./",
							QtWidgets.QFileDialog.ShowDirsOnly
							| QtWidgets.QFileDialog.DontResolveSymlinks)
		self.locLabel.setText(self.saveLoc)
		
	def saveData(self, name):
		#saves existing data under self.saveLoc + name
		#however, name validity and existance should be checked first
		#also if we have any data
		if len(name) == 0:
			return
		if len(self.data) != len(self.xarr):
			return 
		
		if self.formatCombo.currentText() == 'ASCII XY':
			data = pd.DataFrame(list(zip(self.xarr, self.data)))
			data.to_csv(os.path.join(self.saveLoc,name),sep = '\t', header = False, index = False)
		elif self.formatCombo.currentText() == 'ASCII Y':
			data = pd.DataFrame(list(self.data))
			data.to_csv(os.path.join(self.saveLoc,name),sep = '\t', header = False, index = False)
		#the rest will follow
	
	def setExternal(self, state):
		#cancel acquisition and set enabled/disabled  
		#set self.acquiring = False
		self.external = state
		if state:
			self.runButt.setChecked(False)
			if (self.acquiring):
				#wait until stopped
				while(self.idus.status == 'Acqring'):
					pass
				data = self.idus.data
				self.setAcq(False)
				
		for wdg in self.dsbl:
			wdg.setEnabled(not state)
		

		
def AndorExitHandler():
	#QtWidgets.QMessageBox.information(None,window.wlLabel.text() , "Going somewhere?")
	#anything needed before checkout
	pass

	#window.IDusLstnr.stop()
	#window.IDusLstnr.join(timeout=100)


#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	app.aboutToQuit.connect(AndorExitHandler)
	# handle possible command line parameters: address, inport, outport
	args = sys.argv[1:4]
	# port values, if provided, should be integers
	# this errors if they are not
	for i in (1,2):
		if len(args) > i:
			args[i] = int(args[i])

	window = Andor_VI(*args)
	window.show()
	sys.exit(app.exec_())
