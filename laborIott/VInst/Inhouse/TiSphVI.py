
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from laborIott.VInst.SourceVI import Source_VI
from laborIott.adapters.ver2.USBAdapter import USBAdapter
from laborIott.instruments.Inhouse.TiSph import TiSph
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class TiSph_VI(Source_VI):

	def __init__(self):
		super().__init__('TiSph', TiSph, USBAdapter(0xcacc, 0x0002))
		
		
		self.instrum.speed = 50
		self.setWindowIcon(QtGui.QIcon(localPath('ap.ico')))
		self.setWindowTitle("Ti-Sph laser")
		#remove bandwidth widgets
		self.bwLabel.setVisible(False)
		self.bwEdit.setVisible(False)
		self.setBwButt.setVisible(False)

	
		
		#Get values and set fields
		#Disabled in external mode and if not WLreached
		self.motRelButt = QtWidgets.QPushButton("Mot.rel")
		self.motRelButt.resize(70,20)
		#self.dummyWidget.addWidget(self.motRelButt)
		self.motRelButt.setParent(self.dummyWidget)
		self.dsbl += [self.motRelButt]
		self.shutButt.setChecked(self.instrum.shutter == 'open')


		#konnektid
		
		self.setSpButt.clicked.connect(lambda: self.setSpeed(self.spEdit.text()))
		self.motRelButt.clicked.connect(self.releaseMotor)
		
	
		
	
		
	def gotoWL(self,newWL):
		if not self.WLreached.is_set():
			#we could develop a 'stop' routine here
			return
		#also, here the status of the shutter should be checked; if closed, we won't get any feedback so the process is doomed
		if self.instrum.shutter == 'closed':
			if (QtWidgets.QMessageBox.information(self, "NB!", "The shutter is closed. Open?",
			QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel) == QtWidgets.QMessageBox.StandardButton.Ok):
				self.instrum.shutter = 'open'
				self.shutButt.setChecked(True)
			else:
				return
		super().gotoWL(newWL)
		
	def setShutter(self, openit):
		self.instrum.shutter =  'open' if openit else 'closed'

	def setSpeed(self, newspeed):
		#issue a warning if a too low number is entered
		try:
			newSp = int(newspeed)
		except ValueError:
			print("not floatable")
			return #probably a messagebox should do here
		self.instrum.speed = newSp
		self.spEdit.setText("{:.1f}".format(self.instrum.speed))
	
	def releaseMotor(self):
		#force release motor (done automatically during normal ops)
		self.instrum.status = 'release'
		




#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	#	
	window = TiSph_VI()
	window.show()
	sys.exit(app.exec_())
