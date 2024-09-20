from laborIott.instruments.ver2.Andor.andor import IDus
from laborIott.VInst.SpectroVI import Spectro_VI
from laborIott.adapters.ver2.SDKAdapter import SDKAdapter
from PyQt5 import QtWidgets, QtGui
import os, sys

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class iDus_VI(Spectro_VI):

	def __init__(self, refname="iDus"):
		super().__init__(refname)
		self.setWindowIcon(QtGui.QIcon(localPath('Andor.ico')))
		self.setWindowTitle("iDus camera")
		self.elDarkChk.setVisible(False)



	def connectInstr(self, refname):
		adapter = self.getZMQAdapter(refname)
		if adapter is None:
			adapter = SDKAdapter("atmcd32d_legacy",False)
		self.instrum = IDus(adapter)



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

	def setShutter(self):
			#sets the shutter state according to self.shutButt
			self.instrum.shutter = 'open' if self.shutButt.isChecked() else 'closed'



if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
		
	window = iDus_VI() #you may add a different refname as a parameter
	window.show()
	sys.exit(app.exec_())