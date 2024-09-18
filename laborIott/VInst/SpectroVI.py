import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pandas as pd

from .VInst import VInst
import os



def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

from queue import Queue
from math import log10


class Spectro_VI(VInst):

	def __init__(self, refname = ""):

		# the refname parameter is needed for derived classes which may want to define a different name
		# to use different settings for connection
		super().__init__(localPath('Spectrom.ui'))


		#connect instrument
		self.connectInstr(refname)
	
		#parameetrid
		self.ydata = []
		self.back = []
		self.ref = []
		self.instrum.noAccum = 1
		self.instrum.expTime = 0.5
		self.instrum.acqmode = 'single'
		self.acquiring = False
		self.refLoc = self.saveLoc 
		self.external = False
		self.dataQ = Queue()
		self.dsbl = [self.runButt, self.setParmsButt, self.backChk, self.locButt, self.saveButt, self.formatCombo]
		
		#plot
		self.xdata = self.instrum.wavelengths

		#self.graphicsView.setBackground('w')
		self.plot = self.graphicsView.plot([self.xdata[0], self.xdata[-1]], [0, 1], pen = (255, 131, 0)) #fanta
		#https://pyqtgraph.readthedocs.io/en/latest/api_reference/widgets/plotwidget.html

		#TODO: move overlay handling to the spectrographVI main object
		self.createOverlays(1)

		
		
		#connect section
		self.runButt.clicked.connect(self.run)
		self.coolButt.clicked.connect(self.setCooler) #implement
		self.shutButt.clicked.connect(self.setShutter)
		self.setParmsButt.clicked.connect(self.onSetParms) 
		self.loadRefButt.clicked.connect(self.loadRef)
		self.loadOvlButt.clicked.connect(self.loadOverlay)

		
		#konnektid
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)

	def connectInstr(self, refname):
		#define as separate function so it can be overridden
		#adapter = self.getZMQAdapter(refname)
		#if adapter is None:
		#	adapter = SDKAdapter(localPath("../Inst/atmcd32d_legacy"),False)
		self.instrum = None

	def createOverlays(self, noOverlays):
		#TODO: move overlay handling to the spectrographVI main object
		self.noOverlays = noOverlays
		self.overlays = []
		for i in range(self.noOverlays):
			self.overlays += [self.graphicsView.plot(pen = None)]
		
		


	def onTimer(self):
		
		if self.acquiring and self.instrum.status != 'Acqring': #measurement data arrival 
			datalist = self.instrum.data
			if self.reverseChk.isChecked():
				datalist.reverse() #for sideport camera
			self.setAcq(False)
			
			#back set või lahut.
			if self.backChk.isChecked():
				self.back = datalist
				self.sigChk.setChecked(True)
				self.runButt.setChecked(False)
				if len(self.back) == len(self.ref):
					self.absChk.setEnabled(True)
				self.plot.setData(self.xdata, datalist)
				
			elif self.refChk.isChecked():
				self.sigChk.setChecked(True)
				self.runButt.setChecked(False)
				if len(self.back) == len(datalist):
					self.absChk.setEnabled(True)
					datalist = [datalist[i] - self.back[i] for i in range(len(self.back))]
					self.ref = datalist #ref has back subbed already
					self.refLabel.setText('<local>')
				self.plot.setData(self.xdata, datalist)
			else:
				if len(self.back) == len(datalist):
					if not self.absChk.isChecked():
						self.ydata = [datalist[i] - self.back[i] for i in range(len(datalist))]
					else:
						#calculate absorption
						self.ydata = []
						for i in range(len(datalist)):
							R = self.ref[i]
							S = (datalist[i] - self.back[i])
							if R > 0 and S > 0:
								self.ydata += [log10(R) - log10(S)]
							else:
								self.ydata += [0]

				else:
					self.ydata = datalist
				self.plot.setData(self.xdata, self.ydata)
				if self.external:
					self.dataQ.put([self.xdata, self.ydata])
			

			
			if self.runButt.isChecked():
				self.instrum.status = 'start'
				#print("Sending start again")
				self.setAcq(True)
				
		#display the temperature & status
		temp = self.instrum.temperature
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
			self.instrum.status = 'start'
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
			self.instrum.expTime = exp
			self.expEdit.setText("%.3f" % self.instrum.expTime)
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
			self.instrum.noAccum = noAcc
			self.instrum.acqmode = 'single' if (noAcc < 2) else 'accum'
			self.noAccEdit.setText(str(self.instrum.noAccum))
		except ValueError:
			self.noAccEdit.setText("#err")
			
	def onSetParms(self):
		self.setExpTime(self.expEdit.text())
		self.setNoAccum(self.noAccEdit.text())

			
	def setCooler(self):
		if (self.coolButt.isChecked()):
			try:
				temp = int(self.tempEdit.text())
			except ValueError:
				self.tempEdit.setText("#err")
				self.coolButt.setChecked(False)
				return 
			self.instrum.temperature = temp
		else:
			self.instrum.temperature =  None
	
	def setShutter(self):
		self.instrum.shutter = 'open' if self.shutButt.isChecked() else 'closed'
	
	def getX(self):
		return self.xdata
		
	def setSaveLoc(self, loc):
		self.saveLoc = loc
		self.locLabel.setText(self.saveLoc)
		self.refLoc = self.saveLoc

	def loadRef(self):
		fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Load reference', self.refLoc)[0]
		if fname:
			try:
				spc = pd.read_csv(fname, sep = '\t', header = None)
				'''
				if we have two cols, take the second
				if one, take this, more is suspicious
				'''
				no_cols = spc.shape[1]
				if no_cols in (1,2):
					if len(spc[no_cols - 1]) == len(self.ydata):
						self.ref = list(spc[no_cols - 1]) #list needed?
						self.absChk.setEnabled(True)
						self.refLabel.setText(os.path.basename(fname))#fname.split('/')[-1])
						self.refLoc = os.path.dirname(fname)
					else:
						print("spectrum size doesn't match",len(spc[no_cols - 1]),len(self.ydata))

				else:
					print("not sure what this is")

			except:
				print("Hmmm..can't open this")

	def loadOverlay(self):
			fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Load overlay', self.saveLoc)[0]
			if fname:
				try:
					spc = pd.read_csv(fname, sep = '\t', header = None)
					if spc.shape[1] == 2:
						try:
							scale = float(self.ovlScaleEdit.text())
						except ValueError:
							scale = 1.0

						self.overlays[0].setData(spc[0],spc[1]*scale)
						self.overlays[0].setPen('b')
					else:
						self.overlays[0].setPen(None)
						print("can't interpret overlay file")

				except:
					self.overlays[0].setPen(None)
					print("Hmmm..can't open this")

	def keyPressEvent(self, e):
		#get autoRange setting [x,y]
		autoState =  self.graphicsView.getPlotItem().getViewBox().getState()['autoRange']
		if e.key() == QtCore.Qt.Key_Escape:
			if self.acquiring and not self.external:
				pass #stop acquisition, think about how to do it
		elif e.key() == QtCore.Qt.Key_F3:
			pass #toggle continuous run
		elif e.key() == QtCore.Qt.Key_F5:
			pass #start/stop single run
		elif e.key() == QtCore.Qt.Key_F6: #toggle y auto/fixed scale (x auto will be enabled too)
			if autoState[1]: #autoscale on
				self.graphicsView.disableAutoRange('y')
			else:
				self.graphicsView.enableAutoRange('xy')
		elif e.key() == QtCore.Qt.Key_F9: #fit in window
			if not autoState[0]: #x autoscale off		
				self.graphicsView.setXRange(min(self.xdata), max(self.xdata))
			if not autoState[1]: #y autoscale off		
				self.graphicsView.setYRange(min(self.ydata), max(self.ydata))
			#toggle btw autoscale and min-max of the graph



	
	def setExternal(self, state):
		#cancel acquisition and set enabled/disabled  

		if state:
			self.runButt.setChecked(False)
			if (self.acquiring):
				#wait until stopped
				while(self.instrum.status == 'Acqring'):
					pass
				data = self.instrum.data
				self.setAcq(False)
		super().setExternal(state)
		

		



#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
		
	window = Spectro_VI() #you may add a different refname as a parameter
	window.show()
	sys.exit(app.exec_())
