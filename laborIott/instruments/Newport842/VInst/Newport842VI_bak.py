import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

#import pandas as pd

from laborIott.adapters.serial import SerialAdapter
from laborIott.instruments.Newport842.Inst.Newport842 import Newport842
import numpy as np

'''
autoscale
attenuator
wl - lugeda sisse
siis mean ja stdev paremini formattida
siis saving
'''


Ui_MainWindow, QMainWindow = uic.loadUiType('Powermeter.ui')

class Newport842_VI(QMainWindow, Ui_MainWindow):

	def __init__(self):
		super(Newport842_VI, self).__init__()
		self.setupUi(self)
		
		#kuidas port ette anda?
		self.pwrmtr = Newport842(SerialAdapter("COM3",baudrate=115200, timeout = 0.3))
		
		#initialize some fields
		self.pwrWlEdit.setText("{:.1f}".format(self.pwrmtr.wl))
		self.attnChk.setChecked(self.pwrmtr.attenuator)
		
		
		self.pwr = []
		self.collecting = False
		#external stuff
		self.external = False
		self.dsbl = [self.pwrWlButt, self.startButt, self.resetButt, self.attnChk]
		
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(500)
		self.pwrWlButt.clicked.connect(self.setPwrWL)
		self.startButt.clicked.connect(self.startSeries)
		self.resetButt.clicked.connect(self.resetSeries)
		self.attnChk.toggled.connect(self.attnChange)
		self.aScaleChk.toggled.connect(self.aScaleChange)
		
	def onTimer(self):
		#powermeter
		inval = self.pwrmtr.power
		if type(inval) is float:
			inval *= 1e6 #measure in uW
			self.pwrLabel.setText("{:.2f} uW".format(inval))
			if self.collecting:
				self.pwr.append(inval) #collect power while acquiring
				#update mean and stdev vals
				self.NLabel.setText("{}".format(len(self.pwr)))
				self.meanLabel.setText("{}".format(np.mean(self.pwr))) #mida siia?
				self.stdevLabel.setText('%s' % float('%.2g' % np.var(self.pwr)))
					
	def setPwrWL(self):
		try:
			newWL = float(self.pwrWlEdit.text())
		except ValueError:
			print("not floatable")
			return 
		self.pwrmtr.wl = newWL
		self.pwrWlEdit.setText("{:.1f}".format(self.pwrmtr.wl))
		
	def attnChange(self):
		self.pwrmtr.attenuator = int(self.attnChk.isChecked())
		
	def aScaleChange(self):
		self.pwrmtr.scale = 'Auto' if self.aScaleChk.isChecked() else '100u'
		
	def startSeries(self):
		self.startButt.setText("Cont" if self.collecting else "Pause")
		self.collecting = not self.collecting

	def resetSeries(self):
		if not self.collecting:
			self.startButt.setText("Start")
		self.pwr = []
		
	#TODO: saving
		
	def setExternal(self, state):
		#cancel moving and set enabled/disabled  
		self.collecting = False
		self.resetSeries()
		self.external = state
		self.setEnable(not state)
		for wdg in self.dsbl:
			wdg.setEnabled(not state)
		
def ExitHandler():
	#QtWidgets.QMessageBox.information(None,window.wlLabel.text() , "Going somewhere?")
	#anything needed before checkout
	pass



#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	app.aboutToQuit.connect(ExitHandler)
	window = Newport842_VI()
	window.show()
	sys.exit(app.exec_())
