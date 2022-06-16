
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

#import pandas as pd
from threading import Event

from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.adapters.ZMQAdapter import ZMQAdapter
from laborIott.instruments.Chirascan.Inst.Chirascan import ChiraScan
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

Ui_MainWindow, QMainWindow = uic.loadUiType(localPath('ChiraScan.ui'))


class Chira_VI(QMainWindow, Ui_MainWindow):

	def __init__(self,address= None, inport= None, outport = None):
		super(Chira_VI, self).__init__()
		self.setupUi(self)

		#instrumendi tekitamine
		#if remoteaddress is None:
		if address is None:
			# local instrument
			self.chira = ChiraScan(SDKAdapter(localPath("../Inst/FOPCIUSB"),False)) 
		else:
			# connect to remote instrument
			# default port is 5555
			inp = 5555 if inport is None else inport
			outp = inp if outport is None else outport
			self.idus = ChiraScan(ZMQAdapter("chira", address, inp, outp))
		
		self.WLreached = Event()
		self.WLreached.set()
		
		self.askTempCounter = 0
		
		#Get values and set fields
		#Disabled in external mode and if not WLreached
		self.dsbl = [self.goWlButt, self.shutButt, self.setBwButt]
		self.external = False
		self.wlEdit.setText("{:.1f}".format(self.chira.wavelength))
		


		#konnektid
		self.goWlButt.clicked.connect(lambda: self.gotoWL(self.wlEdit.text()))
		self.shutButt.clicked.connect(lambda: self.setShutter(self.shutButt.isChecked()))
		self.setBwButt.clicked.connect(self.setBW)
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)
		
		
	def onTimer(self):
		#handle goingtoWL
		if not self.WLreached.isSet():
			#check arrival
			self.wlEdit.setStyleSheet("color: red")
			if self.chira.stepsmissing[0] == 0:
				if not self.external:
					self.setEnable(True)
				self.WLreached.set()
				self.wlEdit.setStyleSheet("color: black")
				self.wlEdit.setText("{:.1f}".format(self.chira.wavelength))
		#get temperatures every Nth time
		if not self.askTempCounter:
			self.monoTempLabel.setText("{:.2f} °C".format(self.chira.monotemp))
			self.cuvTempLabel.setText("{:.2f} °C".format(self.chira.cuvettetemp))
			self.askTempCounter = 10
		else:
			self.askTempCounter -=1

		
	def gotoWL(self,newWL):
		#oot aga nüüd ma mõtlen, et seda (vist) peaks saama ka väljast kutsuda, et kas siis anda talle optsionaalselt mingi pärameeter ka, et kui on, siis kasutatakse või.
		if not self.WLreached.isSet(): #should be greyed, though
			return
		try:
			newWL = float(newWL)
		except ValueError:
			print("not floatable")
			return #TODO: nendega midagi
		self.setEnable(False)
		self.chira.wavelength = newWL
		self.WLreached.clear()
		
	def setShutter(self, openit):
		self.chira.shutter =  'open' if openit else 'closed'

	def setBW(self):#TODO: ,newBW = None)
		try:
			newBW = float(self.bwEdit.text())
		except ValueError:
			print("not floatable")
			return #probably a messagebox should do here
		self.chira.bandwidth = newBW
		self.bwEdit.setText("{:.1f}".format(self.chira.bandwidth))
		
	def setEnable(self, state):
		for wdg in self.dsbl:
			wdg.setEnabled(state)
			
	def setExternal(self, state):
		#cancel moving and set enabled/disabled  
		#set self.acquiring = False
		self.external = state
		#check if not goingtoWL
		self.setEnable(not state)
		
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
	# handle possible command line parameters: address, inport, outport
	args = sys.argv[:3]
	# port values, if provided, should be integers
	# this errors if they are not
	for i in (1,2):
		if len(args > i):
			args[i] = int(args[i])
	window = Chira_VI(*args)
	window.show()
	sys.exit(app.exec_())
