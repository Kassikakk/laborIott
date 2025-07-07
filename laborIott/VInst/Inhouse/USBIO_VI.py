
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from threading import Event
from laborIott.VInst.VInst import VInst
from laborIott.adapters.USBAdapter import USBAdapter
from laborIott.instruments.Inhouse.USBIO import USBIO
from time import sleep
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class USBIO_VI(VInst):

	def __init__(self):
		super().__init__(localPath('USBIO.ui'),'USBIO', USBIO, USBAdapter(0xcacc, 0x0004))
		#self.setupUi(self)

		
		
		#Get values and set fields
		#Disabled in external mode and if not WLreached
		self.dsbl += [self.ODButt, self.shutButt]
		#self.wlEdit.setText("{:.2f}".format(self.tisph.wavelength))
		self.ODreached = Event()
		self.ODreached.set()
		


		#konnektid
		self.ODButt.clicked.connect(lambda: self.setOD(self.ODEdit.text()))
		self.shutButt.clicked.connect(lambda: self.setShutter(self.shutButt.isChecked()))
		self.instrum.freq1 = 300
		self.setOD(0.05)
		
		
		
	#def onTimer(self):
		#will be needed if there is a separate way to change OD
		#super().onTimer()
		
	def onReconnect(self):
		super().onReconnect()
		if self.instrum.connected:
			self.instrum.freq1 = 300
			#self.setOD(self.ODEdit.text()) #või midagi sellist

						
		
	def setOD(self,newOD):
		#siin nüüd teha midagi
		try:
			newOD = float(newOD)
		except ValueError:
			return
		self.ODreached.clear()
		#we go about 3 OD units in 1.2s, so 0.4s per unit
		dOD = abs(newOD - self.instrum.OD)
		self.instrum.OD = newOD
		sleep(0.5*dOD) #let's put 0.5s just in case
		self.ODLabel.setText("{:.2f}".format(self.instrum.OD))
		self.ODreached.set()
		#who should do the waiting and for how long?
		
	def setShutter(self, openit):
		self.instrum.setpin(0,int(openit))
		#self.tisph.shutter =  'open' if openit else 'closed'

	def getStatus(self):
		#returns the status of the instrument, if it has one
		super().getStatus()
		self.statusDict['USBIO']= {'OD': "{:.2f}".format(self.instrum.OD)}
		return self.statusDict
		




#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	#	
	window = USBIO_VI()
	window.show()
	sys.exit(app.exec_())
