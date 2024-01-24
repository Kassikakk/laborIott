
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from threading import Event
from laborIott.VInst.VInst import VInst
from laborIott.adapters.ver2.USBAdapter import USBAdapter
from laborIott.instruments.Inhouse.TiSph import TiSph
import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class TiSph_VI(VInst):

	def __init__(self):
		super().__init__(localPath('TiSph.ui'))
		#self.setupUi(self)

		#how to make it a bit nicer?
		adapter = self.getZMQAdapter('TiSph')
		if adapter is None:
			adapter = USBAdapter(0xcacc, 0x0002)
		self.tisph = TiSph(adapter)
		
		self.tisph.speed = 50

		self.WLreached = Event()
		self.WLreached.set()
		
		
		#Get values and set fields
		#Disabled in external mode and if not WLreached
		self.dsbl += [self.goWlButt, self.shutButt, self.setSpButt]
		self.wlEdit.setText("{:.1f}".format(self.tisph.wavelength))
		


		#konnektid
		self.goWlButt.clicked.connect(lambda: self.gotoWL(self.wlEdit.text()))
		self.shutButt.clicked.connect(lambda: self.setShutter(self.shutButt.isChecked()))
		self.setSpButt.clicked.connect(lambda: self.setSpeed(self.spEdit.text()))
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)
		
		
	def onTimer(self):
		#handle goingtoWL
		self.wlLabel.setText("{:.1f}".format(self.tisph.wavelength))
		if not self.WLreached.is_set():
			#check arrival
			self.wlLabel.setStyleSheet("color: red")
			if self.tisph.status == 'stopped':
				if not self.external:
					self.setEnable(True)
				self.WLreached.set()
				self.wlLabel.setStyleSheet("color: black")
						
		
	def gotoWL(self,newWL):
		#oot aga nüüd ma mõtlen, et seda (vist) peaks saama ka väljast kutsuda, et kas siis anda talle optsionaalselt mingi pärameeter ka, et kui on, siis kasutatakse või.
		if not self.WLreached.isSet(): #should be greyed, though
			return
		#also, here the status of the shutter should be checked; if closed, we won't get any feedback so the process is doomed
		try:
			newWL = float(newWL)
		except ValueError:
			print("not floatable")
			return #TODO: nendega midagi
		self.setEnable(False)
		self.tisph.wavelength = newWL
		self.WLreached.clear()
		
	def setShutter(self, openit):
		self.tisph.shutter =  'open' if openit else 'closed'

	def setSpeed(self, newspeed):
		#issue a warning if a too low number is entered
		try:
			newSp = float(newspeed)
		except ValueError:
			print("not floatable")
			return #probably a messagebox should do here
		self.tisph.speed = newspeed
		self.spEdit.setText("{:.1f}".format(self.tisph.speed))
		




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
