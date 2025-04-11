#Hakkame välja skemeerima üldisemat excitit
import sys, os
from PyQt5 import QtCore, QtWidgets

from threading import Thread, Event
from queue import Queue
from time import sleep, time
from scipy.interpolate import interp1d
from math import log10
import numpy as np
import pandas as pd
import importlib as imlb

from laborIott.procedures.VProc import VProc #või no tegelikult...


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class ExcitProc(VProc): #(pole nimes veel kindel)

#siin peaks nüüd olema see signaalide defineerimine
#aga vist eriti neid ei tule või siis scanni lõpetus
	setExternalMode = QtCore.pyqtSignal(bool)

	def  __init__(self):
		super().__init__(localPath('Excit.ui'))

		#parse ini file to define the instruments
		instr_conf = self.getConfigSection("VInst", "Excit")
		self.instr_list = ['exsrc','spectrom', 'powerm','attnr','spectro2','positnr'] #and so on
		for instr_name in self.instr_list:
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
						print('Module not found: laborIott.'  + module[0])
						
			exec('self.{} = '.format(instr_name) + astr)
			if astr != 'None':
				exec('self.{}.show()'.format(instr_name))
				exec('self.setExternalMode.connect(self.{}.setExternal)'.format(instr_name))
				exec('self.show_{}Butt.clicked.connect(self.{}.show)'.format(instr_name, instr_name))
			else:
				exec('self.show_{}Butt.setEnabled(False)'.format(instr_name))
		#we should now have self.source, self.spectrom and so on


		self.scanning = Event()
		self.scanThread = None
		self.scandataQ = Queue()
		self.plot = self.graphicsView.plot([0, 1], [0, 0], pen=(255, 131, 0))  # fanta
		self.plotx = [[0, 1]]
		self.ploty = [[0, 0]]
		self.extPwrData = None  # external powerdata
		self.extraMoveData = None  # extra move data
		self.refSum = None  # reference sum
		self.refPower = None  # reference power
		self.dsbl += [self.startEdit, self.stepEdit, self.stopEdit, self.spcChk, self.pwrChk, self.sxminEdit,
					 self.sxmaxEdit, self.pwrRadioBox]
		self.setEnable(True)
		self.startButt.clicked.connect(self.onStart)
		self.setExternalMode.connect(self.setExternal)
		self.spcChk.clicked.connect(lambda: self.setExternal(False))
		self.pwrChk.clicked.connect(lambda: self.setExternal(False))
		self.locButt.clicked.connect(self.onGetLoc)
		self.saveButt.clicked.connect(lambda: self.saveData(self.nameEdit.text()))
		self.powerRefFile.clicked.connect(self.getPowerData) #TODO: this needs a better approach
		self.extraMoveFile.clicked.connect(self.getExtraMoveData) #TODO: this needs a better approach
		self.takeRefChk.clicked.connect(self.checkRefData)

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
			wparms['attnShut'] = self.attnShutChk.isChecked() and self.attnr is not None
			wparms['spcShut'] = self.spcShutChk.isChecked() and self.spectrom is not None
			wparms['srcShut'] = self.srcShutChk.isChecked() and self.exsrc is not None
			wparms['refpos'] = None
			wparms['sigpos'] = None
			wparms['takeRef'] = False
			if self.takeRefChk.isChecked() and self.positnr is not None:
				if self.positnr.sigref[0] is not None and self.positnr.sigref[1] is not None:
					wparms['takeRef'] = True
					#kumbapidi on need?
					wparms['refpos'] = self.positnr.sigref[1]
					wparms['sigpos'] = self.positnr.sigref[0]
					#TODO: sigpos needs to be initialized for extraMove, too
				else:
					QtWidgets.QMessageBox.information(self, "NB!", "Check reference positions")
					return

			wparms['extraMove'] = (not self.extraMoveNone.isChecked()) and self.positnr is not None
			if wparms['extraMove']:
				#we should have a list with extraMove data
				wparms['extraMoveData'] = self.extraMoveData
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
					self.spectrom.setSaveLoc(spcFolder)
				if wparms['usePwr']:
					pwrFolder = os.path.join(baseFolder, 'pwr')
					os.mkdir(pwrFolder)
					self.powerm.setSaveLoc(pwrFolder)
				if self.spectro2 is not None: #also create spectro2 folders if needed
					spcFolder = os.path.join(baseFolder, 'wl')
					os.mkdir(spcFolder)
					self.spectro2.setSaveLoc(spcFolder)
				



			self.plotx[0] = np.array([wparms['startwl'] + i * wparms['stepwl'] for i in range(wparms['nopoints'])])
			#self.plotx[0] = np.arange(wparms['startwl'],wparms['stopwl'],wparms['stepwl']) #is the same?
			self.ploty[0] = np.zeros(wparms['nopoints'])
			# open source shutter
			if self.exsrc is not None:
				self.exsrc.setShutter('open')

			self.scanThread = Thread(target=self.scanProc, args= (wparms,))
			self.startButt.setText("Stop")
			self.xdata = []
			self.ydata = []
			self.refSum = None  
			self.refPower = None 
			self.setExternalMode.emit(True) 
			self.startTime = time()
			self.scanning.set()
			sleep(1) #make sure the shutter has opened
			self.scanThread.start()

	
	def scanProc(self, wparms):

		'''
		Worker thread routine
		use thread-safe methods:
		-access external functions via signals, e.g. VIcommand mechanisms (important if functions access UI elements)
		-get data via queue
		-observe states via events


		'''

		curwl = wparms['startwl']
		ind = 0
		xmoveind = 0 #for extraMoveData
		while np.sign(wparms['stepwl']) * curwl <= np.sign(wparms['stepwl']) * wparms['stopwl']:  # enable negative step

			if self.exsrc is not None:
				self.exsrc.VIcommand.emit({'gotoWL':curwl})
				while self.exsrc.WLreached.is_set(): #first wait for the motion to start
					pass
				while not self.exsrc.WLreached.is_set(): #then wait it to stop.
					if not self.scanning.is_set():
						return
				#print("WL reached", curwl)
				#looks like it also works if we're already there

			
			#if we are taking reference spectra or pow value from a different position (location, cuvette angle)
			#refpos, sigpos - relevant position values; takeref - switch, self.positnr
			for i,pos in enumerate([wparms['refpos'], wparms['sigpos']]):
				isRef = (i == 0)
				#do refpos first, then sigpos can be used to level-check
				if not wparms['takeRef'] and isRef:
					continue
				#let's do the positioning here
				extraMoveNeeded = wparms['extraMove'] and not isRef #only do extraMove for sigpos
				if extraMoveNeeded:
					pos = [pos[i] + wparms['extraMoveData'][xmoveind][i] for i in range(len(pos))]
					#print(pos)
					xmoveind += 1
					if xmoveind >= len(wparms['extraMoveData']):
						xmoveind = 0
				if wparms['takeRef'] or extraMoveNeeded: #kas on vaja võtta ka ref?
					self.positnr.VIcommand.emit({'gotoPos':[pos, False]})#what if position already?
					while self.positnr.posReached.is_set(): #first wait for the motion to start
						if not self.scanning.is_set():
							return
					while not self.positnr.posReached.is_set(): #then wait it to stop.
						if not self.scanning.is_set():
							return
				

				#open the ODshutter here (and other shutters if needed)
				#we also should have wparms['keepShutterOpen'] if the wl change is quick
				if wparms['attnShut']:
					self.attnr.VIcommand.emit({'setShutter':1})
				
				if wparms['spcShut']:
					self.spectrom.VIcommand.emit({'setShutter':1})

				if wparms['srcShut']:
					self.exsrc.VIcommand.emit({'setShutter':1})


				if wparms['usePwr']:
					# adjust powermeter wl
					self.powerm.VIcommand.emit({'setPwrWL':curwl})
					# start powermeter series + reset previous
					self.powerm.VIcommand.emit({'setCollect':[True, True]})



				# wait a while
				if self.spectro2 is not None:
					self.spectro2.VIcommand.emit({'run':None})

				if wparms['useSpc']:  # Spectrometer determines the time
					# idus shutter open?
					self.spectrom.VIcommand.emit({'run':None})
					# wait for data arrival
					while self.spectrom.dataQ.empty():
						if not self.scanning.is_set():
							return
					# idus shutter close?
					xData, spcData = self.spectrom.dataQ.get(False)
				else:
					spcData = None
					startTime = time()
					while (time() < startTime + wparms['pwrTime']):
						if not self.scanning.is_set():
							return

				if self.spectro2 is not None:
					while self.spectro2.dataQ.empty(): #also check that spectro2 has finished
						if not self.scanning.is_set():
							return

				if wparms['usePwr']:
					# stop powermeter series, wait for data
					self.powerm.VIcommand.emit({'setCollect':[False, False]})
					self.powerm.VIcommand.emit({'getData':True}) # mean and dev only 
					while self.powerm.dataQ.empty():
						if not self.scanning.is_set():
							return
					pwrData = self.powerm.dataQ.get(False)  # list of [mean, dev]
					#print("Powerdata received")
					# order powerdata saving as needed (construct name)
					#also take into account ref or sig, if needed
					self.powerm.VIcommand.emit({'saveData':"{:}nm{}.txt".format(curwl,"_ref" if isRef else "")})
				else:
					pwrData = None

				#close shutters here
				if wparms['attnShut']:
					self.attnr.VIcommand.emit({'setShutter':0})
				
				if wparms['spcShut']:
					self.spectrom.VIcommand.emit({'setShutter':0})

				if wparms['srcShut']:
					self.exsrc.VIcommand.emit({'setShutter':0})

				if wparms['useSpc']:  # save the spectral data
					#also take into account ref or sig, if needed
					if wparms['usePwr']:
						spcfilename = "{:}uW{:.4}var{:.3}{}.txt".format(curwl, pwrData[0], pwrData[1],"_ref" if isRef else "")
					else:
						spcfilename = "{:}nm{}.txt".format(curwl,"_ref" if isRef else "")
					self.spectrom.VIcommand.emit({'saveData':spcfilename})
				
				if self.spectro2 is not None:
					self.spectro2.VIcommand.emit({'saveData':spcfilename})

				# calculate and emit (or Queue) results to main thread
				self.VIcommand.emit({'update':[(ind,) + (spcData,) + (pwrData,),isRef]})
				#now the OD correction should happen here

				#for signal measurement we need to check the level and adjust the OD if needed
				#also advance the index and wavelength
				if not isRef:
					while self.scandataQ.empty():
						if not self.scanning.is_set():
								return
					newOD = self.scandataQ.get(False) 
					#print("NewOD=",newOD)
					if newOD is not None:
						#adjust the OD
						self.attnr.VIcommand.emit({'setOD':newOD})
						while not self.attnr.ODreached.is_set(): #wait for the disk to turn
							if not self.scanning.is_set():
								return
					else:
						#move on
						curwl += wparms['stepwl']
						ind += 1

		self.VIcommand.emit({'cleanScan':None})

	def cleanScan(self):
		self.scanning.clear()
		self.startButt.setText("Start")
		if self.exsrc is not None:
				self.exsrc.setShutter('closed')
		self.scanProgBar.setValue(0)
		self.scanProgBar.setFormat("0%%")
		self.setExternalMode.emit(False)
		self.saveData(self.nameEdit.text())
		if self.autoFolderChk.isChecked():
			#go back to parent folder
			self.setSaveLoc(os.path.dirname(self.saveLoc))

	def update(self, data, isRef = False):
		# supposedly called while scanning only
		index, spcData, pwrData = data
		# index is the current index in the scan
		# spcData is the spectral data (or None)
		# pwrData is [mean, dev] or None
		newOD = None #may be needed for level checking

		if spcData is not None:
			spsum = self.getSum(self.spectraX, spcData)
			# figure out power
			power = self.getPwr(1.0 if pwrData is None else pwrData[0], self.plotx[0][index])
			# see what's power & calc excit
			# put into plot
			if isRef:
				# we need to record spsum and power for reference
				self.refSum = spsum
				self.refPower = power
				#we can probably just return here
				return
			#the following is for signal measurement
			if self.refSum is not None:
				# we need to subtract reference from signal
				spsum -= self.refSum
			if self.refPower is not None:
				#we can just use the reference power
				power = self.refPower
			excit = spsum / power
			self.ploty[0][index] = excit
			self.xdata += [self.plotx[0][index]]
			self.ydata += [excit]

			#do level check if needed
			if self.levelCheck.isChecked() and self.attnr is not None:
				try:
					xval = float(self.lvlXEdit.text())
					ctrlval = spcData[np.abs(np.array(self.spectraX) - xval).argmin()]
				except ValueError:
					print("Levelcheck: xval not applicable, using total max")
					ctrlval = max(spcData)
				newOD = self.getODCorr(ctrlval)
	
		elif pwrData is not None:
			if isRef:
				# we need to record power for reference
				self.refPower = pwrData[0]
				return
			power = pwrData[0]
			if self.refPower is not None:
				#we can calculate e.g. absorbance
				power = log10(self.refPower/power)
			self.ploty[0][index] = power
			self.xdata += [self.plotx[0][index]]
			self.ydata += [power]
			#Here also add ydata

		self.scandataQ.put(newOD)
		self.plot.setData(self.plotx[0], self.ploty[0])
		self.saveData(self.nameEdit.text())

		# progress
		# fractional progress
		prg = (index + 1) / len(self.plotx[0])
		progress = int(prg * 100)
		# estimation by time spent
		remmin = int((1 / prg - 1.0) * (time() - self.startTime) / 60)
		self.scanProgBar.setValue(progress)
		self.scanProgBar.setFormat("%d%% (%d min)" % (progress, remmin))


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

	def getODCorr(self, ctrlval):
		#determine new OD for level checking
		#or None if no need to change or not able to determine
		
		OD = self.attnr.instrum.OD
		try:
			minval = float(self.lvlMinEdit.text())
			maxval = float(self.lvlMaxEdit.text())
		except ValueError:
			print("Levelcheck: Check min max fields")
			return None
		if minval >= maxval:
			print("Levelcheck: min > max?")
			return None
		#get applicable OD limits	
		minOD, maxOD = self.attnr.instrum.ODlimits
		if (ctrlval  < minval) and OD > minOD: #can be adjusted lower
			rel = 0.8*maxval / ctrlval
			if(rel > 0):
				OD -= log10(rel)
				if OD < minOD:
					OD = minOD
				print("adjusting lower to {}".format(OD))
				return OD
			else:
				return None
		elif (ctrlval  > maxval) and OD < maxOD: #can be adjusted higher
			rel = ctrlval/(0.8*maxval)
			if (rel > 0):
				OD += log10(rel)
				if OD > maxOD:
					OD = maxOD
				print("adjusting higher to {}".format(OD))
				return OD
			else:
				return None
			
		return None
			

	def getSum(self, x, y):
		# sum y-s from the x values given by fields
		minind = 0
		maxind = len(x)
		min1 = float(self.sxminEdit.text())
		max1 = float(self.sxmaxEdit.text())
		# both need to be between limits and min < max
		# TODO: check this for +-1's here or there
		if (min1 > x[0]) and (max1 < x[-1]) and (min1 < max1):
			step = (x[-1] - x[0]) / (len(x) - 1)
			minind = int((min1 - x[0]) / step)
			maxind = int((max1 - x[0]) / step)
		return sum(y[minind:maxind])

	def getPwr(self, defaultval, wavelen = None):
		if self.powerRefFile.isChecked() and wavelen is not None:  # there may be no power data
			try:
				pwr = interp1d(self.extPwrData[0], self.extPwrData[1])(wavelen)
			except ValueError:  # out of limits
				print("powerref out of limits at {}?".format(wavelen))
				pwr = 1.0
			return pwr
		elif self.powerRefCur.isChecked() and defaultval is not None:
			return defaultval
		else:
			return 1.0
		return pwr

	def getPowerData(self):
		# read external power data file into self.extPwrData
		if self.powerRefFile.isChecked():
			allok = True
			fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Power data file')[0]
			# try:
			data = pd.read_csv(fname, sep='\t', header=None)
			if len(data.columns) == 2:
				self.extPwrData = data
				
			else:
				allok = False
			# except:
			#	allok = False
			if not allok:
				self.powerRefNone.setChecked(True)

	def getExtraMoveData(self):
		# read external extra move data file into self.extraMoveData
		if self.positnr is None:
			self.extraMoveNone.setChecked(True)
			return
		if self.extraMoveFile.isChecked():
			allok = True
			fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Move data file')[0]
			# try:
			data = pd.read_csv(fname, sep='\t', header=None)
			if len(data.columns) == self.positnr.dim:
				self.extraMoveData = []
				for i in range(len(data)):
					addendum = [data[k][i] for k in range(self.positnr.dim)]
					self.extraMoveData += [addendum]
			else:
				allok = False
			# except:
			#	allok = False
			if not allok:
				self.extraMoveNone.setChecked(True)

	def checkRefData(self):
		if self.positnr is None:
			self.takeRefChk.setChecked(False)
			return
		# check if we have reference positions set
		if self.takeRefChk.isChecked():
			if self.positnr.sigref[0] is None or self.positnr.sigref[1] is None:
				self.takeRefChk.setChecked(False)
				QtWidgets.QMessageBox.information(self, "NB!", "Check reference positions")
				return

	def closeEvent(self, event):
		# close subwins and see that no threads are running
		if self.scanning.is_set():
			self.scanning.clear()
			self.scanThread.join(timeout=10)
		for instr_name in self.instr_list:
			exec('if self.{} is not None: self.{}.close()'.format(instr_name,instr_name))
		event.accept()




if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	
	window = ExcitProc()
	window.show()
	sys.exit(app.exec_())