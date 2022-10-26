import sys
#import zmq
#import cloudpickle
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pyqtgraph as pg
import pandas as pd

from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Flame.Inst.Flame import Flame #LabDev folder on siin pathi peal aga kuidas peaks?
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

#import pathlib
#pathlib.Path(__file__).parent.resolve()

#from fittings import  fit_DLorentz, fit_DLorentz_slope

#from multilistener import MultiListener
#from queue import Queue
from threading import Event
#from time import sleep, strftime, time
#import numpy as np
from math import log10

#import Spectra


Ui_MainWindow, QMainWindow = uic.loadUiType(localPath('Flame.ui'))

class Flame_VI(QMainWindow, Ui_MainWindow):

	def __init__(self):
		super(Flame_VI, self).__init__()
		self.setupUi(self)

		#instrumendi tekitamine
		self.flame = Flame(SDKAdapter(localPath("../Inst/OmniDriver32"), False))
		#siin peaks kuidagi adapterivahetust organiseerima vajadusel
		
		#parameetrid
		self.data = []
		self.back = []
		self.ref = []
		self.acquiring = Event() #define as event so other threads can check it
		self.saveLoc = './'
		self.external = False
		
		#plot
		self.xarr = self.flame.wavelengths

		#self.graphicsView.setBackground('w')
		self.plot = self.graphicsView.plot([self.xarr[0],self.xarr[-1]],[0,1], pen = (255,131,0)) #fanta
		
		self.expLabel.setText("%.3f" % self.flame.expTime)
		self.noAccLabel.setText(str(self.flame.noAccum))
		
		
		#connect section
		self.runButt.clicked.connect(self.run)
		self.setParmsButt.clicked.connect(self.onSetParms) 
		self.elDarkChk.clicked.connect(self.setElDark)
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda : self.saveData(self.nameEdit.text()))

		
		#konnektid
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)
		

		
		
		
		
	def onTimer(self):
		
		if len(self.flame.asyncready) > 0: #measurement data arrival 
			datalist = self.flame.data
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
			

			
			if self.runButt.isChecked():
				self.flame.status = 'start'
				#print("Sending start again")
				self.setAcq(True)
				
	def setAcq(self, state):
		if state:
			self.acquiring.set()
		else:
			self.acquiring.clear()
		for wdg in [self.setParmsButt, self.saveButt]:
			wdg.setEnabled(not state)


	def run(self):
		if (self.acquiring.is_set()): #ongoing acquisition
			return
		if self.runButt.isChecked() or self.external:
			#start running
			self.flame.status = 'start'
			#print("Sending start")
			self.setAcq(True)
			
	def onSetParms(self):
		if (self.acquiring.is_set()): #ongoing acquisition
			return
		try:
			exp = float(self.expEdit.text())
			#range
			if (exp <= 0): #flame will recheck itself
				self.expEdit.setText("#low")
				return
			self.flame.expTime = exp
			self.expLabel.setText("%.3f" % self.flame.expTime)
		except ValueError:
			self.expEdit.setText("#err")
		try:
			noAcc = int(self.noAccEdit.text())
			#range
			if (noAcc < 0): 
				self.noAccEdit.setText("#low")
				return
			self.flame.noAccum = noAcc
			self.noAccLabel.setText(str(self.flame.noAccum))

		except ValueError:
			self.noAccEdit.setText("#err")
			
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
		dsbl = [self.runButt, self.setParmsButt, self.backChk, self.elDarkChk, self.locButt, self.saveButt, self.formatCombo]
		if state:
			self.runButt.setChecked(False)
			if (self.acquiring.is_set()):
				#wait until stopped
				while(len(self.flame.asyncready) == 0):
					pass
				data = self.flame.data
				self.setAcq(False)
				
		for wdg in dsbl:
			wdg.setEnabled(not state)
		
	def setElDark(self):
		self.flame.corrElDark = 'on' if self.elDarkChk.isChecked() else 'off'
		
def FlameExitHandler():
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
	app.aboutToQuit.connect(FlameExitHandler)
	window = Flame_VI()
	window.show()
	sys.exit(app.exec_())
