import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from threading import Thread, Event
from time import sleep, strftime, time
import numpy as np
import pandas as pd

from laborIott.instruments.Newport842.VInst.Newport842VI import Newport842_VI





Ui_MainWindow, QMainWindow = uic.loadUiType('Excit.ui')

class SimpleProc(QMainWindow, Ui_MainWindow):
	
	setpowerWL = QtCore.pyqtSignal(float)
	setPwrCollection = QtCore.pyqtSignal(bool, bool)
	getPwrData = QtCore.pyqtSignal(bool)
	savePwrData = QtCore.pyqtSignal(str)
	setExternalMode = QtCore.pyqtSignal(bool)
	updateData = QtCore.pyqtSignal(tuple)
	scanFinished = QtCore.pyqtSignal()
	#start scanmode signal
	#send data to main signal
	

	def __init__(self):
		super(SimpleProc, self).__init__()
		self.setupUi(self) 
		self.powerm = Newport842_VI(False)
		
		self.scanning = Event()
		self.plot = self.graphicsView.plot([0,1],[0,0], pen = (255,131,0)) #fanta
		self.plotx = [[0,1]]
		self.ploty = [[0,0]]
		
		self.dsbl = [self.startEdit, self.stepEdit, self.stopEdit,self.iDusChk, self.pwrChk, self.sxminEdit, self.sxmaxEdit, self.pwrRadioBox, 
		self.locButt, self.nameEdit, self.saveButt, self.formatCombo] #vist e/v kõik peale start nupu (kui mingi view selector just jääb veel
		self.scanThread  = None
		self.startButt.clicked.connect(self.onStart)
		self.showPwrmButt.clicked.connect(lambda: self.powerm.show())
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda : self.saveData(self.nameEdit.text()))
		
		self.setpowerWL.connect(self.powerm.setPwrWL) 
		self.setPwrCollection.connect(self.powerm.setCollect)
		self.getPwrData.connect(self.powerm.getData)
		self.savePwrData.connect(self.powerm.saveData)
		self.setExternalMode.connect(self.powerm.setExternal)
		self.updateData.connect(self.update)
		self.scanFinished.connect(self.cleanScan)
		self.powerm.show()
		
	
	def onStart(self):
		if self.scanning.isSet():
			#end scanning
			self.cleanScan()
			self.scanThread.join()
			
		else:
			#emit signal to subwindows
			#we need to do some initializing
			startwl = float(self.startEdit.text())
			stopwl = float(self.stopEdit.text())
			stepwl =  float(self.stepEdit.text())
			nopoints = int((stopwl-startwl)/stepwl + 1)
			pwrTime = float(self.pwrTimeEdit.text())
			savePwr = self.pwrChk.isChecked()
			
			if nopoints < 1:
				QtWidgets.QMessageBox.information(self, "NB!","The scan has just one point")
				#kuigi tegelikult on ju üks punkt alati?
				return
			#we could also show some checklist here
			self.plotx[0] = np.array([startwl + i*stepwl for i in range(nopoints)])
			self.ploty[0] = np.zeros(nopoints)
			#open Chira shutter
			
			for b in self.dsbl:
				b.setEnabled(False)
			self.scanThread  = Thread(target = self.scanProc, args = (startwl, stopwl, stepwl, pwrTime, savePwr))
			self.startButt.setText("Stop")
			self.setExternalMode.emit(True)
			self.startTime = time()
			self.scanning.set()
			self.scanThread.start()
			
	def scanProc(self, startwl, stopwl, stepwl, pwrTime, savePwr):
		
		curwl = startwl
		ind = 0
		while np.sign(stepwl)*curwl <= np.sign(stepwl)*stopwl: #enable negative step

			#adjust powermeter wl
			self.setpowerWL.emit(curwl)
			
			#start powermeter series + reset previous
			self.setPwrCollection.emit(True,True)
			#wait a while
			startTime = time()
			while (time() < startTime + pwrTime):
				if not self.scanning.isSet():
					return
					
			#stop powermeter series, wait for data
			self.setPwrCollection.emit(False, False)
			self.getPwrData.emit(True) #mean and dev only
			while self.powerm.dataQ.empty():
				if not self.scanning.isSet():
						return
			pwrData = self.powerm.dataQ.get(False) #list
			
			#order powerdata saving as needed (construct name)
			if savePwr:
				self.savePwrData.emit(str(curwl) + "nm.txt")
			self.updateData.emit((ind,) + pwrData)
			#calculate and emit (or Queue) results to main thread
			#note that saving could in principle be invoked from main thread as well
			
			#including progress data
			curwl += stepwl
			ind +=1
		self.scanFinished.emit()
			
			
	def cleanScan(self):
		self.scanning.clear()
		for b in self.dsbl:
			b.setEnabled(True)
		self.startButt.setText("Start")
		self.scanProgBar.setValue(0)
		self.scanProgBar.setFormat("0%%")
		self.setExternalMode.emit(False)
		self.saveData(self.nameEdit.text())
		
	def update(self,data):
		self.ploty[0][data[0]] = data[1]
		self.plot.setData(self.plotx[0],self.ploty[0])
		#progress
		#fractional progress
		prg = (data[0] + 1)/len(self.plotx[0])
		progress = int(prg*100)
		#estimation by time spent
		remmin = int((1/prg - 1.0) * (time() - self.startTime) / 60)
		self.scanProgBar.setValue(progress)
		self.scanProgBar.setFormat("%d%% (%d min)" % (progress, remmin))
		self.saveData(self.nameEdit.text())
		
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
		self.powerm.can_close = True
		self.powerm.close()
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
