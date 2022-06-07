#imports
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from queue import Queue
from threading import Thread, Event
from time import sleep, strftime, time
import numpy as np
import pandas as pd

from laborIott.instruments.Chirascan.VInst.ChiraVI import Chira_VI
from laborIott.instruments.Andor.VInst.AndorVI import Andor_VI
from laborIott.instruments.Newport842.VInst.Newport842VI import Newport842_VI





Ui_MainWindow, QMainWindow = uic.loadUiType('Excit.ui')

class ChiraExcit(QMainWindow, Ui_MainWindow):

	def __init__(self):
		super(ChiraExcit, self).__init__()
		self.setupUi(self) 
		
		#nüüd peaks vist VI-d sisse tõmbama ja äkki showma ka või?
		self.chira = Chira_VI()
		self.andor = Andor_VI()
		self.powerm = Newport842_VI()
		#siis peaks küll ka vaatama, et kas ikka avanesid ja serverlahenduse puhul lisanduvad ka parameetrid
		#no objektid ehk küll avanevad, aga kas ka instrumendid taga on?
		
		self.scanning = Event()
		self.plot = self.graphicsView.plot([0,1],[0,0], pen = (255,131,0)) #fanta
		
		self.disbl = [] #vist e/v kõik peale start nupu (kui mingi view selector just jääb veel
		
		#võibolla neid ei lähe kõiki vaja
		self.scanqueue = Queue() #Parameters to scanthread + signal data arrival
		self.scancommq = Queue() #commands from scanthread
		self.curWLqueue = Queue()#current wl from thread
		self.startTimequeue = Queue()
		self.scanThread  = None
		self.startTime = None
		
		self.startButt.clicked.connect(self.onStart)
		self.axminEdit.textChanged.connect(self.updPlot)
		self.axmaxEdit.textChanged.connect(self.updPlot)
		self.powerRefFile.clicked.connect(self.getPowerData)
		#we need to connect signals to all slots we want to control
		self.chira.show()
		self.andor.show()
		self.powerm.show()
		
	
	def updPlot(self):
		minx = float(self.axminEdit.text())
		maxx = float(self.axmaxEdit.text())
		if maxx > minx:
			#we need to set self.plotx[1] min and max but keep the length
			#can len somehow be 1 here?
			self.plotx[1] = np.arange(minx, maxx, (maxx - minx) / (len(self.plotx[1])))
		plotType = 1 if self.viewSpc.isChecked() else 2 if self.viewPwr.isChecked() else 3 if self.viewTrans.isChecked() else 0
		self.plot.setData(self.plotx[plotType],self.ploty[plotType])
		
	def getSum(self):
		minind = 0
		maxind = len(self.plotx[1])
		min1 = float(self.sxminEdit.text())
		max1 = float(self.sxmaxEdit.text())
		#both need to be between limits and min < max
		#TODO: check this for +-1's here or there
		if (min1 > self.plotx[1][0]) and (max1 < self.plotx[1][-1]) and (min1 < max1):
			step = (self.plotx[1][-1] - self.plotx[1][0]) / (len(self.plotx[1]) - 1)
			minind = int((min1 - self.plotx[1][0]) / step)
			maxind = int((max1 - self.plotx[1][0]) / step)
		return sum(self.ploty[1][minind:maxind])
	
	def getPwr(self):
		if self.powerRefFile.isChecked(): #there may be no power data
			try:
				pwr = interp1d(self.pwrData[0], self.pwrData[1])(float(self.wlLabel.text()))
			except: #out of limits
				pwr = 1.0
			return pwr
		elif self.powerRefCur.isChecked():
			if self.measMode == 1 and self.pwrrefmean is not None:
				return self.pwrrefmean
			elif self.measMode == 2 and self.pwrmean is not None:
				return self.pwrmean
		else:
			return 1.0
		return pwr
		
	def getPowerData(self):
		if self.powerRefFile.isChecked():
			allok = True
			fname = QtGui.QFileDialog.getOpenFileName(self, 'Power data file')[0]
			#try:
			data = pd.read_csv(fname, sep='\t', header = None)
			if len(data.columns) == 2:
				self.pwrData = data
			else:
				allok = False
			#except:
			#	allok = False
			
			if not allok:
				self.powerRefNone.setChecked(True)
				
	def onStart(self):
		if self.scanning.isSet():
			#end scanning
			self.cleanScan()
			self.scanThread.join()
			
		else:
			#we need to do some initializing
			startwl = float(self.startEdit.text())
			stopwl = float(self.stopEdit.text())
			stepwl =  float(self.stepEdit.text())
			nopoints = int((stopwl-startwl)/stepwl + 1)
			
			if nopoints < 1:
				QtWidgets.QMessageBox.information(self, "NB!","The scan has just one point")
				#kuigi tegelikult on ju üks punkt alati?
				return
			#we could also show some checklist here
			self.plotx[0] = np.array([startwl + i*stepwl for i in range(nopoints)])
			self.ploty[0] = np.zeros(nopoints)
			self.plotx[3] = np.array([startwl + i*stepwl for i in range(nopoints)])
			self.ploty[3] = np.zeros(nopoints)
			#open shutter
			self.emit("Chira_Shutter/todev", 'open')
			for b in self.scandim:
				b.setEnabled(False)
			self.scanThread  = Thread(target = self.scanProc)
			self.startButt.setText("Stop")
			self.startTime = int(time())
			self.scanning.set()
			self.scanThread.start()


	def scanProc(self):
		#tegelikult ikka on vist, et tuleb väljastada signaleid ja siis (Eventi vaadata?)
		#ja threadi käigus mingeid muid gui asju ikka cäppida ei või
		#need peaks siis tegelikult parameetritena ette andma
		#let's copy to locals as much as possible
		startwl = float(self.startEdit.text())
		stopwl = float(self.stopEdit.text())
		stepwl =  float(self.stepEdit.text())
		curwl = startwl
		#self.curWLqueue.put(curwl)
		#wl change

		#scan type
		powerSeries =self.pwrChk.isChecked()
		spcMeasure = self.iDusChk.isChecked()
		keepShutOpen = self.andor.shutButt.isChecked() #way to keep it open if it behaves badly
		#position change:
		refpos = self.refPos #not sure if it makes any sense to double those
		sigpos = self.sigPos
		takeref = self.refCheck.isChecked()
		#level monitor / OD adjust: Not implemented


		while np.sign(stepwl)*curwl <= np.sign(stepwl)*stopwl: #enable negative step

			#adjust powermeter wl
			if powerSeries:
				self.scancommq.put(("PwrWL/todev", curwl))
				
			#goto wl
			self.scancommq.put(("Chira_WL/todev", curwl))
			self.goingtoWL.set()
			
			while self.goingtoWL.isSet():
				if not self.scanning.isSet():
					return
			
			for i,pos in enumerate([refpos, sigpos]):
				#do refpos first, then sigpos can be used to level-check
				if takeref: #kas on vaja võtta ka ref?
					self.scancommq.put(("Cuvette_angle/todev", pos)) #what if position already?
					self.goingtoPos.set()
					while self.goingtoPos.isSet():
						if not self.scanning.isSet():
							return
				else:
					if i == 0: #muidu ainult signal point (ja ei mingit käsku liigutamiseks)
						continue
				#shutters
				if spcMeasure and not keepShutOpen:
					self.scancommq.put(("IdusShutter/todev", 'open'))
				#if there are any more shutters, open them, too
				self.curWLqueue.put((curwl, i if takeref else 2)) #set next wl for UI
				#we should also signal if this is sig or ref but also if there is any separate S/R 

				#start acquisition
				if spcMeasure:
					self.scancommq.put(("IdusStatus/todev", 'start'))
					#print("Start given")
				else:
					self.startTimequeue.put(time())

				self.acquiring.set()
				while self.acquiring.isSet():
					if not self.scanning.isSet():
						return 

				#close shutters
				if spcMeasure and not keepShutOpen:
					self.scancommq.put(("IdusShutter/todev", 'closed'))
				
			curwl += stepwl

	def cleanScan(self):
		#non-blocking cleanup after scan
		self.scanning.clear()
		while not self.scancommq.empty():
			self.scancommq.get(False)
		for b in self.scandim:
			b.setEnabled(True)
		if self.iDusChk.isChecked():
			self.onIdusShutter() #set the shutter according to button state
		self.onChiraShutter()
		self.startButt.setText("Start")
		self.scanProgBar.setValue(0)
		self.scanProgBar.setFormat("0%%")
		#save the scan preview
		self.spc.addSpc(self.ploty[0].tolist(), start = self.plotx[0][0],step = self.plotx[0][1]- self.plotx[0][0],  comment = "Scan preview")
		self.spc.writeSpc(self.resultfile)
		
	def setProgress(self):
		start = float(self.startEdit.text())
		stop = float(self.stopEdit.text())
		step =  float(self.stepEdit.text())
		curwl = float(self.wlLabel.text())
		#ok, this is very approximate, but
		if self.iDusChk.isChecked():
			timestep = float(self.expEdit.text()) * int(self.noAccEdit.text())
		else:
			timestep = float(self.pwrtimeEdit.text()) + float(self.stepEdit.text())*0.2 #very approximately
		
		#fractional progress
		prg = (curwl - start)/(stop - start)
		#current scan result index
		ind = int((curwl - start)/step)
		#percent
		progress = int(prg*100)
		#remmin = int((stop - curwl) * timestep/ (step*60))
		#estimation by time spent
		remmin = int((stop - curwl) * (int(time())-self.startTime) / ((curwl-start + step)*60))
		self.scanProgBar.setValue(progress)
		self.scanProgBar.setFormat("%d%% (%d min)" % (progress, remmin))
		return ind
		





def myExitHandler():
	#QtWidgets.QMessageBox.information(None,window.wlLabel.text() , "Going somewhere?")
	#stopime threadid?
	pass


#needed for running from within Spyder etc.
if not QtWidgets.QApplication.instance():
	app = QtWidgets.QApplication(sys.argv)
else:
	app = QtWidgets.QApplication.instance()
app.aboutToQuit.connect(myExitHandler)
window = ChiraExcit()
window.show()
sys.exit(app.exec_())
