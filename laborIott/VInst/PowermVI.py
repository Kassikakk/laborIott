import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic


from .VInst import VInst

import numpy as np
from threading import Event
from queue import Queue


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)



class Powerm_VI(VInst):

	'''
	Let's try the timer version first until I remember what was the reasoning behind using the thread
	Well, I think it was because sometimes it took a long time to return data for the Newport842
	Though it is not clear why and what to do about it. Normally the timeout was 0.3s, however one might 
	wanna try with 0.1s as well.

	'''

	def __init__(self, refname, instrument, adapter):

		
		super().__init__(localPath('Powermeter.ui'),refname, instrument, adapter)
		#this also makes the first connection so make sure when to actually call it

		self.ydata = []
		self.collecting = False
		self.acquiring = False
		self.dataQ = Queue()

		#initialize some fields
		self.pwrWlEdit.setText("{:.1f}".format(self.instrum.wl))
		self.attnChk.setChecked(self.instrum.attenuator)
				
		#external stuff
		self.dsbl += [self.pwrWlButt, self.startButt, self.resetButt, self.attnChk]

		#connects
		self.pwrWlButt.clicked.connect(lambda: self.setPwrWL(self.pwrWlEdit.text()))
		self.startButt.clicked.connect(lambda: self.setCollect(not self.collecting))
		self.resetButt.clicked.connect(self.resetSeries)
		self.attnChk.toggled.connect(self.attnChange)
		self.aScaleChk.clicked.connect(self.aScaleChange)


	def onTimer(self):
		super().onTimer()
		if self.acquiring: #well in fact, this is just for checking
			print("collision")
			return
		self.acquiring = True
		value = self.instrum.power
		if type(value) is float:
			valuW = value*1e6 #measure in uW
			self.pwrLabel.setText("{:.2f} uW".format(valuW))
			if self.collecting:
				self.ydata.append(valuW) #collect power while acquiring
				#update mean and stdev vals
				self.NLabel.setText("{}".format(len(self.ydata)))
				self.meanLabel.setText("{}".format(np.mean(self.ydata))) #mida siia?
				self.stdevLabel.setText('%s' % float('%.2g' % np.std(self.ydata)))
		self.acquiring = False

	def setPwrWL(self, value):
		#try to convert to float
		try:
			newWL = float(value)
		except ValueError:
			print("not floatable")
			return 
		self.instrum.wl = newWL
		self.pwrWlEdit.setText("{:.1f}".format(self.instrum.wl))

		
	def attnChange(self):
		self.instrum.attenuator = self.attnChk.isChecked()

		
	def aScaleChange(self):
		self.instrum.scale = 'Auto' 

		
	def setCollect(self, state, clearOnStart = False):
		
		if(state and clearOnStart):
			self.ydata = []
		self.startButt.setText("Pause" if state else "Cont")
		self.collecting = state


	def resetSeries(self):
		if not self.collecting:
			self.startButt.setText("Start")
		self.ydata = []
	
	def getData(self,meanDevOnly = True):
		if meanDevOnly:
			self.dataQ.put((np.mean(self.ydata),np.var(self.ydata)))
		else:
			self.dataQ.put(self.ydata)
		return self.ydata

		
	def setExternal(self, state):
		#stop collecting (thread remains working)  
		self.collecting = False
		self.resetSeries()
		super().setExternal(state)

	def getStatus(self):
		#returns the status of the instrument, if it has one
		super().getStatus()
		self.statusDict['Powermeter']= {'Current reading':"{:.2f} uW".format(self.instrum.power*1e6), 
								  'Wavelength': "{:.1f}".format(self.instrum.wl),
								  'Attenuator': self.instrum.attenuator,
								  'Scale': "{},{}".format(self.instrum.scale[0], 'Auto' if self.instrum.scale[1] else 'Fixed'),
								  'Number of readings': len(self.ydata),
								  'Mean': "{:.2f}".format(np.mean(self.ydata)) if len(self.ydata) else '0',	
								  'Stdev': "{:.2f}".format(np.var(self.ydata)) if len(self.ydata) else '0'}
		#scale should somehow be added, but it is not clear how to do it
		return self.statusDict
