import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from threading import Thread, Event
from time import sleep, strftime, time
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd

#from laborIott.instruments.Newport842.VInst.Newport842VI import Newport842_VI as Newport_VI
from laborIott.instruments.Newport1830.VInst.Newport1830VI import Newport1830_VI as Newport_VI
from laborIott.instruments.Andor.VInst.KymeraVI import AndorKymera_VI
from laborIott.instruments.Chirascan.VInst.ChiraVI import Chira_VI

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class SimpleProc(*uic.loadUiType(localPath('Excit.ui'))):
	
	setpowerWL = QtCore.pyqtSignal(float)
	setPwrCollection = QtCore.pyqtSignal(bool, bool)
	getPwrData = QtCore.pyqtSignal(bool)
	savePwrData = QtCore.pyqtSignal(str)
	setExternalMode = QtCore.pyqtSignal(bool)
	updateData = QtCore.pyqtSignal(tuple)
	scanFinished = QtCore.pyqtSignal()
	
	startIdus = QtCore.pyqtSignal(bool)
	saveSpcData = QtCore.pyqtSignal(str)
	
	setChiraShutter = QtCore.pyqtSignal(bool)
	setChiraWL = QtCore.pyqtSignal(float)
	#start scanmode signal
	#send data to main signal
	#what we need for Chira? setChiraShutter, setChiraWL, vist cõik?
	

	def __init__(self):
		super(SimpleProc, self).__init__()
		self.setupUi(self) 
		self.powerm = Newport_VI(False)
		self.andor = AndorKymera_VI()
		self.chira = Chira_VI()
		
		self.scanning = Event()
		self.scanThread  = None
		self.plot = self.graphicsView.plot([0,1],[0,0], pen = (255,131,0)) #fanta
		self.plotx = [[0,1]]
		self.ploty = [[0,0]]
		self.spectraX = self.andor.getX() #get the current x scale
		self.extPwrData = None #external powerdata
		
		#widget status
		self.dsbl = [self.startEdit, self.stepEdit, self.stopEdit,self.spcChk, self.pwrChk, self.sxminEdit, self.sxmaxEdit, self.pwrRadioBox, 
		self.locButt, self.nameEdit, self.saveButt, self.formatCombo] #vist e/v kõik peale start nupu (kui mingi view selector just jääb veel
		self.setWidgetState(False) #no scanning
		self.startButt.clicked.connect(self.onStart)
		self.showPwrmButt.clicked.connect(lambda: self.powerm.show())
		self.showSpctrmButt.clicked.connect(lambda: self.andor.show())
		self.showChiraButt.clicked.connect(lambda: self.chira.show())
		
		self.spcChk.clicked.connect(lambda: self.setWidgetState(False))
		self.pwrChk.clicked.connect(lambda: self.setWidgetState(False))
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda : self.saveData(self.nameEdit.text()))
		
		#outer connections
		self.setpowerWL.connect(self.powerm.setPwrWL)
		self.setPwrCollection.connect(self.powerm.setCollect)
		self.getPwrData.connect(self.powerm.getData)
		self.savePwrData.connect(self.powerm.saveData)
		
		self.startIdus.connect(self.andor.run)
		self.saveSpcData.connect(self.andor.saveData)
		
		self.setChiraShutter.connect(self.chira.setShutter)
		self.setChiraWL.connect(self.chira.gotoWL)
		
		self.setExternalMode.connect(self.powerm.setExternal)
		self.setExternalMode.connect(self.andor.setExternal)
		self.setExternalMode.connect(self.chira.setExternal)
		self.updateData.connect(self.update)
		self.scanFinished.connect(self.cleanScan)
		
		#show everything
		self.powerm.show()
		self.andor.show()
		self.chira.show()
		
	def setWidgetState(self, scanstate):
		for b in self.dsbl:
			b.setEnabled(not scanstate)
		if not scanstate:
			self.pwrTimeEdit.setEnabled(self.pwrChk.isChecked() and not self.spcChk.isChecked())
			self.powerRefCur.setEnabled(self.pwrChk.isChecked())
			if (self.pwrChk.isChecked() and self.powerRefNone.isChecked()):
				self.powerRefCur.setChecked(True)
			if (not self.pwrChk.isChecked() and self.powerRefCur.isChecked()):
				self.powerRefNone.setChecked(True)
		
	
	def onStart(self):
		if self.scanning.isSet():
			#end scanning
			self.cleanScan()
			self.scanThread.join()
			
		else:
			#emit signal to subwindows
			#we need to do some initializing
			#well there will be problems if not filled or filled wrongly, so...
			try:
				startwl = float(self.startEdit.text())
				stopwl = float(self.stopEdit.text())
				stepwl =  float(self.stepEdit.text())
			except ValueError:
				QtWidgets.QMessageBox.information(self, "NB!","Check start-stop-step fields")
				return
			nopoints = int((stopwl-startwl)/stepwl + 1)
			pwrTime = float(self.pwrTimeEdit.text())
			usePwr = self.pwrChk.isChecked()
			useSpc = self.spcChk.isChecked()
			self.spectraX = self.andor.getX()  #update
			
			if nopoints < 1:
				QtWidgets.QMessageBox.information(self, "NB!","The scan has just one point")
				#kuigi tegelikult on ju üks punkt alati?
				return
			#we could also show some checklist here
			self.plotx[0] = np.array([startwl + i*stepwl for i in range(nopoints)])
			self.ploty[0] = np.zeros(nopoints)
			#open Chira shutter
			self.setChiraShutter.emit(True)
			
			self.setWidgetState(True)
			self.scanThread  = Thread(target = self.scanProc, args = (startwl, stopwl, stepwl, pwrTime, useSpc, usePwr))
			self.startButt.setText("Stop")
			self.setExternalMode.emit(True)
			self.startTime = time()
			self.scanning.set()
			self.scanThread.start()
			
	def scanProc(self, startwl, stopwl, stepwl, pwrTime, useSpc, usePwr):
		
		curwl = startwl
		ind = 0
		while np.sign(stepwl)*curwl <= np.sign(stepwl)*stopwl: #enable negative step
			
			self.setChiraWL.emit(curwl)
			#self.chira.WLreached.wait() #vat'uvitav, kas see töötab?
			
			if usePwr:
				#adjust powermeter wl
				self.setpowerWL.emit(curwl)
				#start powermeter series + reset previous
				self.setPwrCollection.emit(True,True)
				
			#wait a while
			if useSpc: #Spectrometer determines the time
				#idus shutter open?
				self.startIdus.emit(True) #reserve false for abort?
				#wait for data arrival
				while self.andor.dataQ.empty():
					if not self.scanning.isSet():
						return
				#idus shutter close?
				spcData = self.andor.dataQ.get(False)
				#aga kuidas siin selle x-skaalaga on?
			else:
				spcData = None
				startTime = time()
				while (time() < startTime + pwrTime):
					if not self.scanning.isSet():
						return
						
			if usePwr:
				#stop powermeter series, wait for data
				self.setPwrCollection.emit(False, False)
				self.getPwrData.emit(True) #mean and dev only
				while self.powerm.dataQ.empty():
					if not self.scanning.isSet():
							return
				pwrData = self.powerm.dataQ.get(False) #list
				#order powerdata saving as needed (construct name)
				self.savePwrData.emit("{:}nm.txt".format(curwl))
			else:
				pwrData = None
				
			if useSpc: #save the spectral data
				if usePwr:
					spcfilename = "{:}uW{:.4}var{:.3}.txt".format(curwl, pwrData[0], pwrData[1])
				else:
					spcfilename = "{:}nm.txt".format(curwl)
				self.saveSpcData.emit(spcfilename)

			
			#calculate and emit (or Queue) results to main thread
			self.updateData.emit((ind,) + (spcData,) + (pwrData,))
			#note that saving could in principle be invoked from main thread as well
			curwl += stepwl
			ind +=1
		self.scanFinished.emit()
			
			
	def cleanScan(self):
		self.scanning.clear()
		self.setWidgetState(False)
		self.startButt.setText("Start")
		self.setChiraShutter.emit(False)
		self.scanProgBar.setValue(0)
		self.scanProgBar.setFormat("0%%")
		self.setExternalMode.emit(False)
		self.saveData(self.nameEdit.text())
		
	def update(self,data):
		#supposedly called while scanning only
		index, spcData, pwrData = data

		if spcData is not None:
			spsum = self.getSum(self.spectraX, spcData)
			#figure out power 
			power = self.getPwr(pwrData[0])
			#see what's power & calc excit
			#put into plot
			self.ploty[0][index] = spsum / power
		elif pwrData is not None:
			self.ploty[0][index] = pwrData[0]
		self.plot.setData(self.plotx[0],self.ploty[0])
		self.saveData(self.nameEdit.text())
		
		#progress
		#fractional progress
		prg = (index + 1)/len(self.plotx[0])
		progress = int(prg*100)
		#estimation by time spent
		remmin = int((1/prg - 1.0) * (time() - self.startTime) / 60)
		self.scanProgBar.setValue(progress)
		self.scanProgBar.setFormat("%d%% (%d min)" % (progress, remmin))
		
	def getSum(self,x,y):
		#sum y-s from the x values given by fields
		minind = 0
		maxind = len(x)
		min1 = float(self.sxminEdit.text())
		max1 = float(self.sxmaxEdit.text())
		#both need to be between limits and min < max
		#TODO: check this for +-1's here or there
		if (min1 > x[0]) and (max1 < x[-1]) and (min1 < max1):
			step = (x[-1] - x[0]) / (len(x) - 1)
			minind = int((min1 - x[0]) / step)
			maxind = int((max1 - x[0]) / step)
		return sum(y[minind:maxind])
	
	def getPwr(self,defaultval):
		if self.powerRefFile.isChecked(): #there may be no power data
			try:
				pwr = interp1d(self.extPwrData[0], self.extPwrData[1])(float(self.wlLabel.text()))
			except: #out of limits
				pwr = 1.0
			return pwr
		elif self.powerRefCur.isChecked() and defaultval is not None:
			return defaultval
		else:
			return 1.0
		return pwr
		
	def getPowerData(self):
		#read external power data file into self.extPwrData
		if self.powerRefFile.isChecked():
			allok = True
			fname = QtGui.QFileDialog.getOpenFileName(self, 'Power data file')[0]
			#try:
			data = pd.read_csv(fname, sep='\t', header = None)
			if len(data.columns) == 2:
				self.extPwrData = data
			else:
				allok = False
			#except:
			#	allok = False
			
			if not allok:
				self.powerRefNone.setChecked(True)
	
	
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
		
		if self.formatCombo.currentText() == 'ASCII XY':
			data = pd.DataFrame(list(zip(self.plotx[0], self.ploty[0])))
			data.to_csv(os.path.join(self.saveLoc,name),sep = '\t', header = False, index = False)
		elif self.formatCombo.currentText() == 'ASCII Y':
			data = pd.DataFrame(list(self.ploty[0]))
			data.to_csv(os.path.join(self.saveLoc,name),sep = '\t', header = False, index = False)
		
	def closeEvent(self, event):
		#close subwins and see that no threads are running
		if self.scanning.isSet():
			self.scanning.clear()
			self.scanThread.join(timeout = 10)
		self.powerm.can_close = True
		self.powerm.close()
		self.andor.close()
		self.chira.close()
		event.accept()

def ExitHandler():
	#QtWidgets.QMessageBox.information(None,window.wlLabel.text() , "Going somewhere?")
	#seems like we need to close the thread here as destructor is never called
	#note that this is only called if it is a main window
	pass
	

if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	app.aboutToQuit.connect(ExitHandler)
	window = SimpleProc()
	window.show()
	sys.exit(app.exec_())
