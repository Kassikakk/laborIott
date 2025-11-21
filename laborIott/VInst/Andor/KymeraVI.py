from laborIott.VInst.Andor.iDusVI import iDus_VI
from laborIott.adapters.SDKAdapter import SDKAdapter
#from laborIott.adapters.ZMQAdapter import ZMQAdapter
from laborIott.instruments.Andor.kymera import IDusKymera
from PyQt5 import QtWidgets
from laborIott.VInst.Andor.KymeraDlg import Ui_KymeraDialog #pyuic5 generated dialog
import os, sys


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

'''
In this case we are dealing with the I2C connected spectrometer, so basically 
there is just 1 instrument, the camera
'''

class AndorKymera_VI(iDus_VI):
	
	def __init__(self):
		super().__init__("Kymera",IDusKymera,SDKAdapter("atmcd32d_legacy",False))
		

		self.dlg = QtWidgets.QDialog()
		self.kymDlg = Ui_KymeraDialog()
		self.kymDlg.setupUi(self.dlg)
		
		self.dsbl += [self.kymDlg.cWlEdit, self.kymDlg.focusEdit, self.kymDlg.filterCombo, self.kymDlg.gratingCombo] #also add kymDlg widgets
		
		self.spectromButt.setEnabled(True)
		
		#initialize self.kymDlg 4 fields
		self.kymDlg.cWlEdit.setText("%.3f" % self.instrum.centerpos)
		self.kymDlg.focusEdit.setText("%d" % self.instrum.focus)
		
		fdict = self.instrum.filterdict
		self.kymDlg.filterCombo.addItems(list(fdict.keys()))
		self.kymDlg.filterCombo.setCurrentText(list(fdict.keys())[list(fdict.values()).index(self.instrum.filter)])
		
		gdict = self.instrum.gratingdict
		self.kymDlg.gratingCombo.addItems(list(gdict.keys()))
		self.kymDlg.gratingCombo.setCurrentText(list(gdict.keys())[list(gdict.values()).index(self.instrum.grating)])
		
		self.spectromButt.clicked.connect(self.dlg.show) #_exec annab modaalse
		
		self.kymDlg.cWlButt.clicked.connect(lambda: self.setCenterWL(self.kymDlg.cWlEdit.text()))
		self.kymDlg.focusButt.clicked.connect(lambda: self.setFocus(self.kymDlg.focusEdit.text()))
		self.kymDlg.filterCombo.currentIndexChanged.connect(self.setFilter)
		self.kymDlg.gratingCombo.currentIndexChanged.connect(self.setGrating)
	
		
	
		
	def setCenterWL(self, value):
		#try to convert to float
		try:
			value = float(value)
		except ValueError:
			print("not floatable")
			return 
		self.instrum.centerpos = value
		self.kymDlg.cWlEdit.setText("%.3f" % self.instrum.centerpos)
		#also change wavelength scale
		self.xdata = self.instrum.wavelengths
		
	def setFocus(self, value):
		#try to convert to int
		try:
			value = int(value)
		except ValueError:
			print("not intable")
			return 
		self.instrum.focus = value
		self.kymDlg.focusEdit.setText("%d" % self.instrum.focus)
		
	def setFilter(self, i):
		#note that i here is combobox index, not the filter number (which should mostly be i+1)!
		#hence for any outside call, this function needs to be modified
		filtno = self.instrum.filterdict[self.kymDlg.filterCombo.currentText()]
		self.instrum.filter = filtno
		
	def setGrating(self, i):
		#i is combobox index again
		#hence for any outside call, this function needs to be modified
		gratno = self.instrum.gratingdict[self.kymDlg.gratingCombo.currentText()]
		self.instrum.grating = gratno
		#the focus also seems to change when grating is changed
		self.kymDlg.focusEdit.setText("%d" % self.instrum.focus)
		#also change wavelength scale
		self.xdata = self.instrum.wavelengths
		
	def getStatus(self):
		#returns the status of the instrument, if it has one
		super().getStatus()
		self.statusDict['Spectrometer']['Type'] = 'Kymera 193i'
		self.statusDict['Spectrometer']['Grating'] = self.kymDlg.gratingCombo.currentText()
		self.statusDict['Spectrometer']['Center WL'] = self.instrum.centerpos
		self.statusDict['Spectrometer']['Range'] = "{:.1f}..{:.1f}".format(self.xdata[0], self.xdata[-1])
		self.statusDict['Spectrometer']['Filter'] = self.kymDlg.filterCombo.currentText()
		self.statusDict['Spectrometer']['Focus steps'] = self.instrum.focus
		
		return self.statusDict
		
		
		



#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	window = AndorKymera_VI() #refname may be added here
	window.show()
	sys.exit(app.exec_())
