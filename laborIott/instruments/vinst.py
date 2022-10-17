import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pandas as pd
import userpaths


from laborIott.adapters.ZMQAdapter import ZMQAdapter

import os


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

#ok, but how do we treat the ui part
# 1) added later 2) some basic ui that can be replaced? In the latter case we need to use the scheme which allows for late connection of .ui
#I would say that we need two classes VInst ->Saving_VI. Although some might say, just log everything in any case, so there could be saving automatically included as well.


class VInst(QtWidgets.QMainWindow):

	def __init__(self, uifile, address= None, inport= None, outport = None):
		super(VInst, self).__init__()
		uic.loadUi(localPath(uifile), self)
		#we can determine some widgets here
		self.locButt = self.findChild(QtWidgets.QPushButton, 'locButt')
		if self.locButt is not None:
			self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt = self.findChild(QtWidgets.QPushButton, 'saveButt')
		self.nameEdit = self.findChild(QtWidgets.QLineEdit, 'nameEdit')
		if self.saveButt is not None and self.nameEdit is not None:
			self.saveButt.clicked.connect(lambda: self.saveData(self.nameEdit.text()))
		self.xdata = None
		self.ydata = None

		#what do we do here to determine adapter / instrument?
		self.external = False
		self.dsbl = []
		self.saveLoc = userpaths.get_my_documents()


	def connectInstr(self, address, inport, outport):
		#instrumendi tekitamine
		if address is None:
			# local instrument
			self.idus = IDus(SDKAdapter(localPath("../Inst/atmcd32d_legacy"), False))
		else:
			# connect to remote instrument
			# default port is 5555
			inp = 5555 if inport is None else inport
			outp = inp if outport is None else outport
			self.idus = IDus(ZMQAdapter("iDus", address, inp, outp))

	def setExternal(self, state):
		self.external = state
		# do any waiting and stopping needed to enter the second state
		for wdg in self.dsbl:
			wdg.setEnabled(not state)


	def onGetLoc(self):
		self.saveLoc = QtWidgets.QFileDialog.getExistingDirectory(self, "Save location:", self.saveLoc,
							QtWidgets.QFileDialog.ShowDirsOnly
							| QtWidgets.QFileDialog.DontResolveSymlinks)
		#self.locLabel.setText(self.saveLoc)

	def saveData(self, name):
		# saves existing data under self.saveLoc + name
		# however, name validity and existence should be checked first
		# also if we have any data
		if len(name) == 0:
			return
		if self.xdata is not None and (len(self.xdata) != len(self.ydata)):
			return

		if self.formatCombo.currentText() == 'ASCII XY':
			data = pd.DataFrame(list(zip(self.xdata, self.ydata)))
			data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False)
		elif self.formatCombo.currentText() == 'ASCII Y':
			data = pd.DataFrame(list(self.ydata))
			data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False)




