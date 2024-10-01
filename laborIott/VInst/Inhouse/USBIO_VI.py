
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from threading import Event
from laborIott.VInst.VInst import VInst
from laborIott.adapters.ver2.USBAdapter import USBAdapter
from laborIott.instruments.Inhouse.USBIO import USBIO
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
		


		#konnektid
		self.ODButt.clicked.connect(lambda: self.setOD(self.ODEdit.text()))
		self.shutButt.clicked.connect(lambda: self.setShutter(self.shutButt.isChecked()))
		self.instrum.freq1 = 300
		self.setOD(1500)
		
		
		
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
			newOD = int(newOD)
		except ValueError:
			return
		self.instrum.OD = int(newOD)
		self.ODLabel.setText("{}".format(self.instrum.OD))
		
	def setShutter(self, openit):
		self.instrum.setpin(0,int(openit))
		#self.tisph.shutter =  'open' if openit else 'closed'

	
		




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
