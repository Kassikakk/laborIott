from laborIott.instruments.Andor.andor import IDus
from laborIott.VInst.SpectroVI import Spectro_VI
from laborIott.adapters.SDKAdapter import SDKAdapter
from PyQt5 import QtWidgets, QtGui
import os, sys

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class iDus_VI(Spectro_VI):

	def __init__(self, refname = "iDus", instrument = IDus, adapter = SDKAdapter("atmcd32d_legacy",False)):
		super().__init__(refname, instrument, adapter)
		self.setWindowIcon(QtGui.QIcon(localPath('Andor.ico')))
		self.setWindowTitle("iDus camera")
		self.elDarkChk.setVisible(False)




	def showTemperature(self):
		#display the temperature & status
		temp = self.instrum.temperature
		if(temp[1]): #if not acquiring
			self.tempLabel.setText("{}°C / {}".format(temp[1], temp[0]))

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

	def setShutter(self,state):
			#sets the shutter state according to self.shutButt
			self.instrum.shutter = 'open' if state else 'closed'

	def onReconnect(self):
		super().onReconnect()
		if self.instrum.connected:
			self.setShutter(self.shutButt.isChecked())
			self.setCooler()



if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
		
	window = iDus_VI() #you may add a different refname as a parameter
	window.show()
	sys.exit(app.exec_())
