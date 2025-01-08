from laborIott.instruments.MCL_MicroStage.MicroStage import MCL_MicroStage
from laborIott.VInst.PositionVI import Position_VI
from laborIott.adapters.SDKAdapter import SDKAdapter
from PyQt5 import QtWidgets, QtGui
import os, sys

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class MCL_VI(Position_VI):

	def __init__(self, refname = "MCL_MS", instrument = MCL_MicroStage, adapter = SDKAdapter("MicroDrive",False)):
		super().__init__(refname, instrument, adapter,2)
		#self.setWindowIcon(QtGui.QIcon(localPath('Andor.ico')))
		self.setWindowTitle("MCL MicroStage")
		#self.elDarkChk.setVisible(False)
		self.resetEncButt.clicked.connect(lambda: self.gotoPos(None))
		

	def centerStage(self): #override
		#move stage to extremes
		poss = []
		for p in [[-100,0],[0,-100],[100,0], [0,100]]:
			self.instrum.pos = p
			while self.instrum.ismoving:
				pass
			poss += [self.instrum.pos]
		self.instrum.pos = [(poss[0][0] + poss[2][0])/2,(poss[1][1] + poss[3][1])/2]
		self.posReached.clear()


if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	#	
	window = MCL_VI()
	window.show()
	sys.exit(app.exec_())