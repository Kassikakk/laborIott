from laborIott.instruments.OceanOptics.Flame import Flame
from laborIott.VInst.SpectroVI import Spectro_VI
from laborIott.adapters.SDKAdapter import SDKAdapter
from PyQt5 import QtWidgets, QtGui
import os,sys

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class Flame_VI(Spectro_VI):

	'''
	Flame spectrometer VI
	Generally works, tests needed for non-normals
	-off-on while connected: seems fine, also with replug while not connected
	-start non-conn then plug and connect: crashes
	-plugout while connected: no disconnect but works when reconnected

	TODO: General question: What needs to be requested (from instrument, from GUI) upon (re)connection?
	(i.e. in onConn)
	
	
	'''

	def __init__(self, refname="Flame"):
		super().__init__(refname, Flame,SDKAdapter("OmniDriver32",False))
		self.setWindowIcon(QtGui.QIcon(localPath('Flame.png')))
		self.setWindowTitle("Flame spectrometer")
		self.coolButt.setVisible(False)
		self.tempEdit.setVisible(False)
		self.tempLabel.setVisible(False)
		self.spectromButt.setVisible(False)
		#connect or disable some controls
		self.elDarkChk.clicked.connect(self.setElDark)


	def setElDark(self):
		#TODO: direct UI dependency doesn't support external access
		self.instrum.corrElDark = 'on' if self.elDarkChk.isChecked() else 'off'

	def onReconnect(self):
		super().onReconnect()
		if self.instrum.connected:
			self.xdata = self.instrum.wavelengths
			self.setElDark()
			#TODO: What else is needed here?
		


if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
		
	window = Flame_VI() #you may add a different refname as a parameter
	window.show()
	sys.exit(app.exec_())
