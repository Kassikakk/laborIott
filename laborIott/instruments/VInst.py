import sys

from PyQt5 import QtWidgets, uic
import pandas as pd
import userpaths
import configparser as cp
from zipfile import ZipFile

from laborIott.adapters.ZMQAdapter import ZMQAdapter

import os
def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)



class VInst(QtWidgets.QMainWindow):
	'''
	The class is supposed to take care of some recurring tasks:
	-saving data (TODO: zip file support)
		-define self.xdata as a list(like) to have x-data
	-selecting adapter: default or network (specify an .ini file with [ZMQ] section for instruments that need it)
	(and put it in local config/laborIott/Inst, filename <refname>.ini)
	-selecting external mode
	-handling the possible other settings in .ini file
	Each instrument is supposed to have a unique refname which is used for settings file and ZMQ connection id
	Note however that a vinst may have multiple instruments (->refnames).

	'''

	def __init__(self, uifile):
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
		self.saveToZip = self.findChild(QtWidgets.QCheckBox,'saveToZip')
		if self.saveToZip is not None:
			self.saveToZip.clicked.connect(self.onZipClick)
			self.dsbl += [self.saveToZip]
		self.useXYFormat = self.findChild(QtWidgets.QCheckBox,'useXYFormat')
		if self.useXYFormat is not None:
			self.dsbl += [self.useXYFormat]
		#account for the possibility of no x-data (but we should have y)
		self.xdata = None
		self.ydata = []

		#should we use an event here?
		self.external = False

		self.saveLoc = userpaths.get_my_documents()

	def getConfigSection(self, section, refname):
		conf_loc = userpaths.get_local_appdata()+ '/laborIott/Inst/'+refname + '.ini'
		conf = cp.ConfigParser()
		#is the file present?
		#print(conf_loc)
		if conf.read(conf_loc) == []:
			#print(conf_loc + " not Found")
			return None
		#has the section?
		return None if not conf.has_section(section) else conf[section]
			

	def getZMQAdapter(self, refname):
		#this will select either the default adapter or ZMQ (possibly some other protocol) if access over LAN is needed
		#so any instrument now should get an adapter through this function
		#the refname argument is because there may be multiple instruments connected to a 
		
		#simple adding seems ok:
		#if any of the following is false, return None
		zmqSection =  self.getConfigSection('ZMQ', refname)
		if zmqSection is None:
			return None
		#no 'active' key or the value is yes
		#print("section found")
		if not zmqSection.getboolean('active', True):
			return None
		#has address
		address = zmqSection.get('address','')
		if len(address) == 0:
			return None
		#print("address ok")
		
		#else construct a ZMQAdapter
		inport = zmqSection.getint('inport',5555)
		outport = zmqSection.getint('outport',inport)
		return ZMQAdapter(refname, address, inport, outport)

	def setEnable(self, state):
		#define separately so VInsts can use it
		for wdg in self.dsbl:
			wdg.setEnabled(state)


	def setExternal(self, state):
		# do any waiting and stopping needed to enter the second state
		#in the child class, then call parent
		self.external = state
		self.setEnable(not state)
		
	def onZipClick(self, zipUsed):
		#We need to change saveLoc here to be a zip file if "save to zip" is used, else a folder
		#We do so by calling onGetLoc; however we also need to revert if selecting fails
		self.onGetLoc()





	def onGetLoc(self):
		if(self.saveToZip.isChecked()):
			self.saveLoc = QtWidgets.QFileDialog.getSaveFileName(self, "Save location:", self.saveLoc,"*.zip")
		else:
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

		#Let's use X data if it's there (in equal amount to Y data) and not explicitly excluded
		useX = self.xdata is not None
		useX &= (self.useXYFormat is None or self.useXYFormat.isChecked())

		if useX and (len(self.xdata) != len(self.ydata)):
			return
		
		formatting = 'ASCII' if self.formatCombo is None else self.formatCombo.currentText()
		zipped = self.saveToZip is not None and self.saveToZip.isChecked()

		if useX:
			data = pd.DataFrame(list(zip(self.xdata, self.ydata)))
		else:
			data = pd.DataFrame(list(self.ydata))

		if formatting == "ASCII":
			if zipped:
				data.to_csv(self.saveLoc, sep='\t', header=False, index=False, mode='a', compression = {'method':'zip', 'archive_name': name})
				#or:
				#with ZipFile(self.saveLoc, mode='w') as zfile:
					#zfile.writestr(name, data.to_csv(sep='\t', header=False, index=False))
			else:
				data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False)
		else:
			b = b''
			form_char = 'q' if formatting[0] == 'l' else formatting[0] #not sure if this is decent enough
			#form_char = {'int':'i', 'longint':'q', 'float':'f', 'double':'d'}[formatting[:formatting.find(' ')]]
			for i, row in data.iterrows():
				for col in data.columns:
					if form_char in 'iq':
						b += struct.pack(form_char, int(row[col]))
					elif form_char in 'df':
						b += struct.pack(form_char, float(row[col]))
					else:
						return #unknown type
			if zipped:
				with ZipFile(self.saveLoc, mode='a') as zfile: #'a' gives error if file exists already, 'w' erases everything else?
					zfile.writestr(name, b)
			else:
				with open(os.path.join(self.saveLoc, name), 'wb') as f:
					f.write(b)





