from laborIott.instruments.Andor.VInst.AndorVI import Andor_VI
from laborIott.adapters.SDKAdapter import SDKAdapter
#from laborIott.adapters.ZMQAdapter import ZMQAdapter
from laborIott.instruments.Andor.Inst.shamrock import Shamrock
from PyQt5 import QtWidgets
from laborIott.instruments.Andor.VInst.ShamrockDlg import Ui_ShamrockDialog #pyuic5 generated dialog
import os, sys


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class IDusShamrock_VI(Andor_VI): #IDusShamrock or AndorShamrock? Can other cameras be used?
	'''
	This instrument is to drive a Shamrock + iDus (or other cämra?) tandem
	specifically if Shamrock is connected via USB separately.
	The I2C connection is slightly more complicated,
	we'll see if we can handle this in the future.
	'''

	def __init__(self):
		super(IDusShamrock_VI, self).__init__()
		#prep the dialog
		self.dlg = QtWidgets.QDialog()
		self.shamDlg = Ui_ShamrockDialog()
		self.shamDlg.setupUi(self.dlg)
		
		self.dsbl += [self.shamDlg.cWlEdit, self.shamDlg.slitEdit, self.shamDlg.cWlButt, 
			self.shamDlg.slitButt, self.shamDlg.flipperCombo, self.shamDlg.gratingCombo] #also add shamDlg widgets
		#create the spectrometer instrument (i.e. the VInst will have 2 instruments)
		adapter = self.getZMQAdapter("Shamrock")
		if adapter is None:
			adapter = SDKAdapter(localPath("../Inst/ShamrockCIF"),False)
		self.shrock = Shamrock(adapter, 26.0, 1024)

		#initialize self.shamDlg 4 fields
		
		self.setWlScale() #also set the scale
		self.shamDlg.slitEdit.setText("{:.1f}".format(self.shrock.slit))

		flpos = self.shrock.flipper
		self.shamDlg.flipperCombo.setCurrentText(flpos)
		if flpos == 'side':
			self.reverseChk.setChecked(True)
		
		gdict = self.shrock.gratingdict
		self.shamDlg.gratingCombo.addItems(list(gdict.keys()))
		self.shamDlg.gratingCombo.setCurrentText(list(gdict.keys())[list(gdict.values()).index(self.shrock.grating)])

		self.spectromButt.setEnabled(True)
		self.spectromButt.clicked.connect(self.dlg.show) #_exec annab modaalse
		self.shamDlg.cWlButt.clicked.connect(lambda: self.setCenterWL(self.shamDlg.cWlEdit.text()))
		self.shamDlg.slitButt.clicked.connect(lambda: self.setSlit(self.shamDlg.slitEdit.text()))
		self.shamDlg.gratingCombo.currentIndexChanged.connect(self.setGrating)
		self.shamDlg.flipperCombo.currentIndexChanged.connect(self.setFlipper)
		#also override setShutter


	def setWlScale(self):
		#a recurring thing, so let's define a function
		self.shamDlg.cWlEdit.setText("{:.3f}".format(self.shrock.centerpos))
		self.xdata = self.shrock.wavelengths
		self.shamDlg.rangeLabel.setText("{:.1f}..{:.1f}".format(self.xdata[0], self.xdata[-1]))

	
	def setCenterWL(self, value):
		#try to convert to float
		try:
			value = float(value)
		except ValueError:
			print("not floatable")
			return 
		self.shrock.centerpos = value
		self.setWlScale()


	def setSlit(self, value):
		#try to convert to float
		try:
			value = float(value)
		except ValueError:
			print("not floatable")
			return 
		self.shrock.slit = value
		self.shamDlg.slitEdit.setText("{:.1f}".format(self.shrock.slit))

	def setGrating(self, i):
		#i is combobox index again
		#hence for any outside call, this function needs to be modified
		gratno = self.shrock.gratingdict[self.shamDlg.gratingCombo.currentText()]
		self.shrock.grating = gratno
		#also change wavelength scale
		#this also includes center wl, interesting how this changes?
		self.setWlScale()
	
	def setFlipper(self, i):
		self.shrock.flipper = ('direct', 'side')[i]
		#well not sure if anything else is needed
		#maybe something related to the camera change?

	#now also the shutter thing needs to be overridden
	def setShutter(self):
		self.shrock.shutter = 'open' if self.shutButt.isChecked() else 'closed'



if __name__ == '__main__':
	#check if run from within what is already a QApplication
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	

	window = IDusShamrock_VI()
	window.show()
	sys.exit(app.exec_())