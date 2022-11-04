import sys

from PyQt5 import QtWidgets, uic
import pandas as pd
import userpaths

from laborIott.adapters.ZMQAdapter import ZMQAdapter

import os
def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)



class VInst(QtWidgets.QMainWindow):
	'''
	The class is supposed to take care of some recurring tasks:
	-saving data (TODO: zip file support)
	-selecting adapter (default or network)
	-selecting external mode

	'''

	def __init__(self, uifile, address= None, inport= None, outport = None):
		super(VInst, self).__init__()
		uic.loadUi(uifile, self) #should we do localPath here or ?
		#we can determine some widgets here
		#probably zip will be added
		self.dsbl = []
		self.locButt = self.findChild(QtWidgets.QPushButton, 'locButt')
		if self.locButt is not None:
			self.locButt.clicked.connect(self.onGetLoc)
			self.dsbl += [self.locButt]
		self.locLabel = self.findChild(QtWidgets.QLabel,'locLabel')
		self.saveButt = self.findChild(QtWidgets.QPushButton, 'saveButt')
		self.nameEdit = self.findChild(QtWidgets.QLineEdit, 'nameEdit')
		if self.saveButt is not None and self.nameEdit is not None:
			self.saveButt.clicked.connect(lambda: self.saveData(self.nameEdit.text()))
			self.dsbl += [self.saveButt, self.nameEdit]
		self.formatCombo = self.findChild(QtWidgets.QComboBox, 'formatCombo')
		if self.formatCombo is not None:
			self.dsbl += [self.formatCombo]
		self.xdata = []
		self.ydata = []
		self.address = address
		self.inport = inport
		self.outport = outport

		#should we use an event here?
		self.external = False

		self.saveLoc = userpaths.get_my_documents()

	def getAdapter(self, def_adapter, refname):
		#this will select either the default adapter or ZMQ (possibly some other protocol) if access over LAN is needed
		if self.address is None:
			return def_adapter
		else:
			inp = 5555 if self.inport is None else self.inport
			outp = inp if self.outport is None else self.outport
			return ZMQAdapter(refname, self.address, inp, outp)


	def setExternal(self, state):
		# do any waiting and stopping needed to enter the second state
		#in the child class, then call parent
		self.external = state
		for wdg in self.dsbl:
			wdg.setEnabled(not state)


	def onGetLoc(self):
		self.saveLoc = QtWidgets.QFileDialog.getExistingDirectory(self, "Save location:", self.saveLoc,
							QtWidgets.QFileDialog.ShowDirsOnly
							| QtWidgets.QFileDialog.DontResolveSymlinks)
		if self.locLabel is not  None:
			self.locLabel.setText(self.saveLoc)

	def saveData(self, name):
		# saves existing data under self.saveLoc + name
		# however, name validity and existence should be checked first
		# also if we have any data
		if len(name) == 0:
			return
		if self.xdata is not None and (len(self.xdata) != len(self.ydata)):
			return

		if self.formatCombo is None or self.formatCombo.currentText() == 'ASCII XY':
			data = pd.DataFrame(list(zip(self.xdata, self.ydata)))
			data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False)
		elif self.formatCombo.currentText() == 'ASCII Y':
			data = pd.DataFrame(list(self.ydata))
			data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False)




