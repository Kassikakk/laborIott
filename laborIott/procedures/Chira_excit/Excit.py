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

#kuidagi tuleks siin see instrumentide eksport, aga see vist initis

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

class ExcitProc(VProc): #(pole nimes veel kindel)

#siin peaks nüüd olema see signaalide defineerimine

	def  __init__(self):
		super().__init__(localPath('Excit.ui'))

		#parse ini file to define the instruments
		instr_conf = self.getConfigSection("Instruments")
		instr_list = ['source','spectrom', 'powerm'] #and so on
		for instr_name in instr_list:
			if instr_name in instr_conf:
				m = imlb.import_module('laborIott.instruments.'  + instr_conf[instr_name][0]) #suppose it's a list of [location,module]
				astr  = "getattr(m,instr_conf['{}'][1])".format(instr_name)
				#ka seda võiks try-da ja kui ei leia, siis None
			else:
				astr = 'None'
			exec('self.{} = '.format(instr_name) + astr)
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



	def setEnable(self, state):
		super().setEnable(state)
		#do extra enablements according to what is present + state
		if not scanstate:
			self.pwrTimeEdit.setEnabled(self.pwrChk.isChecked() and not self.spcChk.isChecked())
			self.powerRefCur.setEnabled(self.pwrChk.isChecked())
			if (self.pwrChk.isChecked() and self.powerRefNone.isChecked()):
				self.powerRefCur.setChecked(True)
			if (not self.pwrChk.isChecked() and self.powerRefCur.isChecked()):
				self.powerRefNone.setChecked(True)

	