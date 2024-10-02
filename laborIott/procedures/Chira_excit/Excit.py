#Hakkame välja skemeerima üldisemat excitit
import sys, os
from PyQt5 import QtCore, QtWidgets

from threading import Thread, Event
from time import sleep, time
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
import importlib as imlb

from laborIott.procedures.VProc import VProc #või no tegelikult...


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class ExcitProc(VProc): #(pole nimes veel kindel)

#siin peaks nüüd olema see signaalide defineerimine
#aga vist eriti neid ei tule või siis scanni lõpetus

	def  __init__(self):
		super().__init__(localPath('Excit.ui'))

		#parse ini file to define the instruments
		instr_conf = self.getConfigSection("VInst", "Excit")
		instr_list = ['exsrc','spectrom', 'powerm','attnr','spectro2','positnr'] #and so on
		for instr_name in instr_list:
			astr = 'None'
			if instr_conf and (instr_name in instr_conf):
				#we should have something comma separated here
				module = instr_conf[instr_name].split(',')
				if len(module) >= 2:
					try:
						m = imlb.import_module('laborIott.'  + module[0]) #suppose it's a list of [location,module]
						astr  = "getattr(m,module[1])()"
					except ModuleNotFoundError:
						#pass # astr remains None if module not found
						print('laborIott.'  + module[0])
			exec('self.{} = '.format(instr_name) + astr)
			if astr != 'None':
				exec('self.{}.show()'.format(instr_name))
		#we should now have self.source, self.spectrom and so on


		self.scanning = Event()
		self.scanThread = None
		self.plot = self.graphicsView.plot([0, 1], [0, 0], pen=(255, 131, 0))  # fanta
		self.plotx = [[0, 1]]
		self.ploty = [[0, 0]]
		self.extPwrData = None  # external powerdata
		self.dsbl += [self.startEdit, self.stepEdit, self.stopEdit, self.spcChk, self.pwrChk, self.sxminEdit,
					 self.sxmaxEdit, self.pwrRadioBox]
		self.setEnable(False)
		self.startButt.clicked.connect(self.onStart)

	def onStart(self):
		if self.scanning.is_set():
			# end scanning
			self.cleanScan()
			self.scanThread.join()

		else:
			#gather all worker thread params to one dict
			wparms = dict()
			try:
				wparms['startwl'] = float(self.startEdit.text())
				wparms['stopwl'] = float(self.stopEdit.text())
				wparms['stepwl'] = float(self.stepEdit.text())
			except ValueError:
				QtWidgets.QMessageBox.information(self, "NB!", "Check start-stop-step fields")
				return
			wparms['nopoints'] = int((wparms['stopwl'] - wparms['startwl']) / wparms['stepwl'] + 1)
			wparms['usePwr'] = self.pwrChk.isChecked() and self.powerm is not None
			wparms['useSpc'] = self.spcChk.isChecked() and self.spectrom is not None
			if wparms['usePwr'] and not wparms['useSpc']:
				try:
					wparms['pwrTime'] = float(self.pwrTimeEdit.text())
				except ValueError:
					QtWidgets.QMessageBox.information(self, "NB!", "Check power collection time")
					return
			if self.spectrom is not None:
				self.spectraX = self.spectrom.getX()  # update
				

			if wparms['nopoints'] < 1:
				QtWidgets.QMessageBox.information(self, "NB!", "The scan has just one point")
				# kuigi tegelikult on ju üks punkt alati?
				return
			
			#TODO: show checklist here

			if self.autoFolderChk.isChecked():
				#the current folder will serve as base
				#find a previously non-existing folder
				n = 0
				while(True):
					baseFolder = os.path.join(self.saveLoc, 'scan_%d' % n)
					if not os.path.isdir(baseFolder):
						break
					n += 1
				#now create three folders and set them as new bases
				os.mkdir(baseFolder)
				self.setSaveLoc(baseFolder)
				if wparms['useSpc']:
					spcFolder = os.path.join(baseFolder, 'spc')
					os.mkdir(spcFolder)
					#ToDO: turn this to setSaveLoc later
					self.spectrom.saveLoc = spcFolder
					self.spectrom.locLabel.setText(spcFolder)
				if wparms['usePwr']:
					pwrFolder = os.path.join(baseFolder, 'pwr')
					os.mkdir(pwrFolder)
					#ToDO: turn this to setSaveLoc later
					self.powerm.saveLoc = pwrFolder
					self.powerm.locLabel.setText(pwrFolder)



			self.plotx[0] = np.array([wparms['startwl'] + i * wparms['stepwl'] for i in range(wparms['nopoints'])])
			#self.plotx[0] = np.arange(wparms['startwl'],wparms['stopwl'],wparms['stepwl']) #is the same?
			self.ploty[0] = np.zeros(wparms['nopoints'])
			# open source shutter
			if self.exsrc:
				self.exsrc.setShutter('open')

			self.setWidgetState(True)
			self.scanThread = Thread(target=self.scanProc, args=(wparms))
			self.startButt.setText("Stop")
			self.setExternalMode.emit(True)
			self.startTime = time()
			self.scanning.set()
			sleep(1) #make sure the shutter has opened
			self.scanThread.start()


	def setEnable(self, state):
		super().setEnable(state)
		#do extra enablements according to what is present + state
		if not state:
			self.pwrTimeEdit.setEnabled(self.pwrChk.isChecked() and not self.spcChk.isChecked())
			self.powerRefCur.setEnabled(self.pwrChk.isChecked())
			if (self.pwrChk.isChecked() and self.powerRefNone.isChecked()):
				self.powerRefCur.setChecked(True)
			if (not self.pwrChk.isChecked() and self.powerRefCur.isChecked()):
				self.powerRefNone.setChecked(True)

	




if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	
	window = ExcitProc()
	window.show()
	sys.exit(app.exec_())