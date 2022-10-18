import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import pandas as pd

from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Newport1830.Inst.Newport1830 import Newport1830
import numpy as np
from threading import Thread, Event
from queue import Queue
import userpaths

'''
autoscale
attenuator
wl - lugeda sisse
siis mean ja stdev paremini formattida
siis saving
'''
def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)



class Newport1830_VI(*uic.loadUiType(localPath('Powermeter.ui'))):
	updateData = QtCore.pyqtSignal(tuple)

	def __init__(self, can_close = True):
		super(Newport1830_VI, self).__init__()
		self.setupUi(self)
		
		#kuidas port ette anda?
		self.pwrmtr = Newport1830(SDKAdapter(localPath("../Inst/usbdll"), False))
		
		#initialize some fields
		self.pwrWlEdit.setText("{:.1f}".format(self.pwrmtr.wl))
		self.attnChk.setChecked(self.pwrmtr.attenuator)
		
		
		self.pwr = []
		self.collecting = False
		#external stuff
		self.external = False
		self.dsbl = [self.pwrWlButt, self.startButt, self.resetButt, self.attnChk]
		self.setSaveLoc(userpaths.get_my_documents())
		self.can_close = can_close
		
		self.measuring = Event()
		self.ops_pending = Event()
		self.thread_stop = Event()
		self.resultQ = Queue()
		self.dataQ = Queue()
		#self.timer = QtCore.QTimer()
		#self.timer.timeout.connect(self.onTimer)
		#self.timer.start(200)
		self.pwrWlButt.clicked.connect(lambda: self.setPwrWL(self.pwrWlEdit.text()))
		self.startButt.clicked.connect(lambda: self.setCollect(not self.collecting))
		self.resetButt.clicked.connect(self.resetSeries)
		self.attnChk.toggled.connect(self.attnChange)
		self.aScaleChk.clicked.connect(self.aScaleChange)
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda : self.saveData(self.nameEdit.text()))
		self.updateData.connect(self.update)
		
		self.workerThread = Thread(target = self.worker)
		self.workerThread.start()
		

	def onTimer(self):
		#check if data arrived?
		while not self.resultQ.empty():
			inval = self.resultQ.get(False)
			if type(inval) is float:
				inval *= 1e6 #measure in uW
				self.pwrLabel.setText("{:.2f} uW".format(inval))
				if self.collecting:
					self.pwr.append(inval) #collect power while acquiring
					#update mean and stdev vals
					self.NLabel.setText("{}".format(len(self.pwr)))
					self.meanLabel.setText("{}".format(np.mean(self.pwr))) #mida siia?
					self.stdevLabel.setText('%s' % float('%.2g' % np.var(self.pwr)))
					
	def update(self, value):
		if type(value[0]) is float:
			valuW = value[0]*1e6 #measure in uW
			self.pwrLabel.setText("{:.2f} uW".format(valuW))
			if self.collecting:
				self.pwr.append(valuW) #collect power while acquiring
				#update mean and stdev vals
				self.NLabel.setText("{}".format(len(self.pwr)))
				self.meanLabel.setText("{}".format(np.mean(self.pwr))) #mida siia?
				self.stdevLabel.setText('%s' % float('%.2g' % np.var(self.pwr)))
			
	def worker(self):
		#where the actual measurement happens
		while(True):
			self.measuring.set()
			#self.resultQ.put(self.pwrmtr.power) #this will block for ~0.5s
			inval = self.pwrmtr.power
			self.measuring.clear()
			self.updateData.emit((inval,))
			#any other processes pending?
			while self.ops_pending.isSet(): #we could use wait() if events were reversed
				pass
			
			if self.thread_stop.isSet(): 
				break
					
	def setPwrWL(self, value):
		#try to convert to float
		try:
			newWL = float(value)
		except ValueError:
			print("not floatable")
			return 
		self.ops_pending.set()
		while self.measuring.isSet():
			pass
		self.pwrmtr.wl = newWL
		w = self.pwrmtr.wl
		self.pwrWlEdit.setText("{:.1f}".format(w))
		self.ops_pending.clear()
		
	def attnChange(self):
		self.ops_pending.set()
		while self.measuring.isSet():
			pass
		self.pwrmtr.attenuator = self.attnChk.isChecked()
		self.ops_pending.clear()
		
	def aScaleChange(self):
		self.ops_pending.set()
		while self.measuring.isSet():
			pass
		self.pwrmtr.scale = 'Auto' 
		self.ops_pending.clear()
		
	def setCollect(self, value, clearOnStart = False):
		
		if(value and clearOnStart):
			self.pwr = []
		self.startButt.setText("Pause" if value else "Cont")
		self.collecting = value


	def resetSeries(self):
		if not self.collecting:
			self.startButt.setText("Start")
		self.pwr = []
	
	def getData(self,meanDevOnly = True):
		if meanDevOnly:
			self.dataQ.put((np.mean(self.pwr),np.var(self.pwr)))
		else:
			self.dataQ.put(self.pwr)
		return self.pwr
		
	#saving
	
	def setSaveLoc(self, loc):
		self.saveLoc = loc
		self.locLabel.setText(self.saveLoc)

	def onGetLoc(self):
		fname = QtWidgets.QFileDialog.getExistingDirectory(self, "Save location:", self.saveLoc,
																  QtWidgets.QFileDialog.ShowDirsOnly
																  | QtWidgets.QFileDialog.DontResolveSymlinks)
		if fname:
			self.setSaveLoc(fname)
	
	def saveData(self, name):
		#saves existing data under self.saveLoc + name
		#however, name validity and existance should be checked first
		#also if we have any data
		if len(name) == 0:
			return
		if len(self.pwr) == 0:
			return 
		
		if self.formatCombo.currentText() == 'ASCII Y':
			data = pd.DataFrame(list(self.pwr))
			#if zip, support it here
			data.to_csv(os.path.join(self.saveLoc,name),sep = '\t', header = False, index = False)
		#the rest will follow
		
	def setExternal(self, state):
		#cancel moving and set enabled/disabled  
		self.collecting = False
		self.resetSeries()
		self.external = state
		
		for wdg in self.dsbl:
			wdg.setEnabled(not state)
			
	def closeEvent(self, event):
		#close the thread here
		if self.can_close:
			self.thread_stop.set()
			self.workerThread.join(timeout=10)
			#print("powerm worker stopped.")
		event.accept()

		
def ExitHandler():
	#QtWidgets.QMessageBox.information(None,window.wlLabel.text() , "Going somewhere?")
	#seems like we need to close the thread here as destructor is never called
	#problem is it won't get called in case of external driving
	
	pass




#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	app.aboutToQuit.connect(ExitHandler)
	window = Newport1830_VI()
	window.show()
	sys.exit(app.exec_())
