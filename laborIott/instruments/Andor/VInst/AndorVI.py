import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pandas as pd

from laborIott.instruments.VInst import VInst

from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.Andor.Inst.andor import IDus
import os
import userpaths


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

from queue import Queue
from math import log10


class Andor_VI(VInst):

	def __init__(self, address= None, inport= None, outport = None):
		super().__init__(localPath('Andor.ui'),address, inport, outport)


		#connect instrument
		self.idus = IDus(self.getAdapter(SDKAdapter(localPath("../Inst/atmcd32d_legacy"), False),"iDus"))

		
		#parameetrid
		self.ydata = []
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
		self.setSaveLoc(userpaths.get_my_documents())
		
		#plot
		self.xdata = self.idus.wavelengths

		#self.graphicsView.setBackground('w')
		self.plot = self.graphicsView.plot([self.xdata[0], self.xdata[-1]], [0, 1], pen = (255, 131, 0)) #fanta

		
		
		#connect section
		self.runButt.clicked.connect(self.run)
		self.coolButt.clicked.connect(self.cooler) #implement
		self.shutButt.clicked.connect(self.setShutter)
		self.setParmsButt.clicked.connect(self.onSetParms) 
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda : self.saveData(self.nameEdit.text()))
		self.loadRefButt.clicked.connect(self.loadRef)

		
		#konnektid
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)
		


	def onTimer(self):
		
		if self.acquiring and self.idus.status != 'Acqring': #measurement data arrival 
			datalist = self.idus.data
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
		return self.xdata
		
	def setSaveLoc(self, loc):
		self.saveLoc = loc
		self.locLabel.setText(self.saveLoc)

	def loadRef(self):
		fn = QtWidgets.QFileDialog.getOpenFileName(self, 'Load reference', self.saveLoc)[0]
		if fn:
			try:
				spc = pd.read_csv(fn, sep = '\t', header = None)
				'''
				if we have two cols, take the second
				if one, take this, more is suspicious
				'''
				no_cols = spc.shape[1]
				if no_cols in (1,2):
					if len(spc[no_cols - 1]) == len(self.ydata):
						self.ref = list(spc[no_cols - 1]) #list needed?
						self.absChk.setEnabled(True)
					else:
						print("spectrum size doesn't match")

				else:
					print("not sure what this is")

			except:
				print("Hmmm..can't open this")


	
	def setExternal(self, state):
		#cancel acquisition and set enabled/disabled  

		if state:
			self.runButt.setChecked(False)
			if (self.acquiring):
				#wait until stopped
				while(self.idus.status == 'Acqring'):
					pass
				data = self.idus.data
				self.setAcq(False)
		super().setExternal(state)
		

		
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
