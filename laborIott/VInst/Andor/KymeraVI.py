from laborIott.instruments.Andor.VInst.AndorVI import Andor_VI
from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.adapters.ZMQAdapter import ZMQAdapter
from laborIott.instruments.Andor.Inst.kymera import IDusKymera
from PyQt5 import QtWidgets
from laborIott.instruments.Andor.VInst.KymeraDlg import Ui_KymeraDialog #pyuic5 generated dialog
import os, sys


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class AndorKymera_VI(Andor_VI):
	
	def __init__(self, refname = "iDus"):
		super(AndorKymera_VI, self).__init__(refname)
		self.dlg = QtWidgets.QDialog()
		self.kymDlg = Ui_KymeraDialog()
		self.kymDlg.setupUi(self.dlg)
		
		self.dsbl += [self.kymDlg.cWlEdit, self.kymDlg.focusEdit, self.kymDlg.filterCombo, self.kymDlg.gratingCombo] #also add kymDlg widgets
		
		self.spectromButt.setEnabled(True)
		
		#initialize self.kymDlg 4 fields
		self.kymDlg.cWlEdit.setText("%.3f" % self.idus.centerpos)
		self.kymDlg.focusEdit.setText("%d" % self.idus.focus)
		
		fdict = self.idus.filterdict
		self.kymDlg.filterCombo.addItems(list(fdict.keys()))
		self.kymDlg.filterCombo.setCurrentText(list(fdict.keys())[list(fdict.values()).index(self.idus.filter)])
		
		gdict = self.idus.gratingdict
		self.kymDlg.gratingCombo.addItems(list(gdict.keys()))
		self.kymDlg.gratingCombo.setCurrentText(list(gdict.keys())[list(gdict.values()).index(self.idus.grating)])
		
		self.spectromButt.clicked.connect(self.dlg.show) #_exec annab modaalse
		
		self.kymDlg.cWlButt.clicked.connect(lambda: self.setCenterWL(self.kymDlg.cWlEdit.text()))
		self.kymDlg.focusButt.clicked.connect(lambda: self.setFocus(self.kymDlg.focusEdit.text()))
		self.kymDlg.filterCombo.currentIndexChanged.connect(self.setFilter)
		self.kymDlg.gratingCombo.currentIndexChanged.connect(self.setGrating)
	
	
	def connectInstr(self, refname):
		#overridden for IDusKymera
		adapter = self.getZMQAdapter(refname)
		if adapter is None:
			adapter = SDKAdapter(localPath("../Inst/atmcd32d_legacy"),False)
		self.idus = IDusKymera(adapter)

		
	
		
	def setCenterWL(self, value):
		#try to convert to float
		try:
			value = float(value)
		except ValueError:
			print("not floatable")
			return 
		self.idus.centerpos = value
		self.kymDlg.cWlEdit.setText("%.3f" % self.idus.centerpos)
		#also change wavelength scale
		self.xdata = self.idus.wavelengths
		
	def setFocus(self, value):
		#try to convert to int
		try:
			value = int(value)
		except ValueError:
			print("not intable")
			return 
		self.idus.focus = value
		self.kymDlg.focusEdit.setText("%d" % self.idus.focus)
		
	def setFilter(self, i):
		#note that i here is combobox index, not the filter number (which should mostly be i+1)!
		#hence for any outside call, this function needs to be modified
		filtno = self.idus.filterdict[self.kymDlg.filterCombo.currentText()]
		self.idus.filter = filtno
		
	def setGrating(self, i):
		#i is combobox index again
		#hence for any outside call, this function needs to be modified
		gratno = self.idus.gratingdict[self.kymDlg.gratingCombo.currentText()]
		self.idus.grating = gratno
		#the focus also seems to change when grating is changed
		self.kymDlg.focusEdit.setText("%d" % self.idus.focus)
		#also change wavelength scale
		self.xdata = self.idus.wavelengths
		
		
		
		



#needed for running from within Spyder etc.
if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	window = AndorKymera_VI() #refname may be added here
	window.show()
	sys.exit(app.exec_())
