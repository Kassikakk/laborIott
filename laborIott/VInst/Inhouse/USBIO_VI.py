
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
		super().__init__(localPath('USBIO.ui'))
		#self.setupUi(self)

		#how to make it a bit nicer?
		adapter = self.getZMQAdapter('USBIO')
		if adapter is None:
			adapter = USBAdapter(0xcacc, 0x0004)
		self.usbio = USBIO(adapter)
		
		#Get values and set fields
		#Disabled in external mode and if not WLreached
		self.dsbl += [self.ODButt, self.shutButt]
		#self.wlEdit.setText("{:.2f}".format(self.tisph.wavelength))
		


		#konnektid
		self.ODButt.clicked.connect(lambda: self.setOD(self.ODEdit.text()))
		self.shutButt.clicked.connect(lambda: self.setShutter(self.shutButt.isChecked()))
		
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)
		
		
	def onTimer(self):
		#handle goingtoWL
		self.ODLabel.setText("{}".format(self.usbio.OD))

						
		
	def setOD(self,newOD):
		self.usbio.OD = int(self.ODEdit.text())
		
	def setShutter(self, openit):
		pass
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
