
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic


from laborIott.VInst.SourceVI import Source_VI

from laborIott.adapters.ver2.SDKAdapter import SDKAdapter
#from laborIott.adapters.ZMQAdapter import ZMQAdapter
from laborIott.instruments.ver2.Chirascan.Chirascan import ChiraScan
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Chira_VI(Source_VI):

	def __init__(self):
		super().__init__('Chira', ChiraScan,SDKAdapter("FOPCIUSB", False))
		#self.setupUi(self)

		
		self.setWindowIcon(QtGui.QIcon(localPath('ap.ico')))
		self.setWindowTitle("Chirascan")
		#remove speed widgets
		self.spLabel.setVisible(False)
		self.spEdit.setVisible(False)
		self.setSpButt.setVisible(False)

		self.monoTempLabel = QtWidgets.QLabel("Monochr. temp: XX.XX °C")
		self.cuvTempLabel = QtWidgets.QLabel("Cuvette temp: XX.XX °C")
		self.monoTempLabel.setParent(self.dummyWidget)
		self.cuvTempLabel.setParent(self.dummyWidget)
		self.cuvTempLabel.move(200,0)
		
		
		self.askTempCounter = 0
		self.continuousUpdate = False
		
		#Get values and set fields
		#Disabled in external mode and if not WLreached
		
		self.wlEdit.setText("{:.1f}".format(self.instrum.wavelength))
		


		#konnektid
		
		self.setBwButt.clicked.connect(lambda: self.setBW(self.bwEdit.text()))
		
		
		
		
	def onTimer(self):
		super().onTimer()
		#get temperatures every Nth time
		if not self.askTempCounter:
			self.monoTempLabel.setText("Monochr. temp: {:.2f} °C".format(self.instrum.monotemp))
			self.cuvTempLabel.setText("Cuvette temp: {:.2f} °C".format(self.instrum.cuvettetemp))
			self.askTempCounter = 10
		else:
			self.askTempCounter -=1

	def onReconnect(self):
		super().onReconnect()
		if self.instrum.connected:
			self.setBW(self.bwEdit.text())
	
	def setBW(self, newBW = None):
		try:
			newBW = float(newBW)
		except ValueError:
			print("not floatable")
			return #probably a messagebox should do here
		self.instrum.bandwidth = newBW
		self.bwEdit.setText("{:.1f}".format(self.instrum.bandwidth))

	def setShutter(self,state):
			#sets the shutter state according to self.shutButt
			self.instrum.shutter = 'open' if state else 'closed'
		




#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	#	
	window = Chira_VI()
	window.show()
	sys.exit(app.exec_())
