import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pandas as pd
from threading import Event
from .VInst import VInst
import os



def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Source_VI(VInst):
	'''
	Base class for tunable source type VI-s
	(Currently) doesn't run standalone (parameters must be supplied)

	'''

	def __init__(self,refname, instrument, adapter):
		super().__init__(localPath("Source.ui"),refname, instrument, adapter)

		self.WLreached = Event()
		self.WLreached.set()

		self.continuousUpdate = True #continuously update wavelength reading or only after transition
		
		
		#Get values and set fields
		#Disabled in external mode and if not WLreached
		self.dsbl += [self.goWlButt, self.shutButt, self.setSpButt, self.setSpButt]
		self.wlEdit.setText("{:.2f}".format(self.instrum.wavelength))
		self.shutButt.setChecked(self.instrum.shutter == 'open')


		#konnektid
		self.goWlButt.clicked.connect(lambda: self.gotoWL(self.wlEdit.text()))
		self.shutButt.clicked.connect(lambda: self.setShutter(self.shutButt.isChecked()))


	def onTimer(self):
		#handle goingtoWL
		if self.continuousUpdate:
			self.wlLabel.setText("{:.2f}".format(self.instrum.wavelength))
		#so the device must be able to give something even when moving
		if not self.WLreached.is_set():
			#check arrival
			self.wlLabel.setStyleSheet("color: red")
			if self.instrum.status == 'stopped':
				if not self.external:
					self.setEnable(True)
				self.WLreached.set()
				self.wlLabel.setStyleSheet("color: black")
				self.wlLabel.setText("{:.2f}".format(self.instrum.wavelength))

	def onReconnect(self):
		#we possibly can't wait it to stop, but let's do what we can
		self.WLreached.set()
		self.wlLabel.setStyleSheet("color: black")
		super().onReconnect()
		if self.instrum.connected:
			#restore wavelength and shutter
			self.gotoWL(self.wlLabel.text())
			self.setShutter(self.shutButt.isChecked())


	def gotoWL(self,newWL):
		if not self.WLreached.is_set() or not self.instrum.connected: #should be greyed, though
			#we could develop a 'stop' routine here
			return
		try:
			newWL = float(newWL)
		except ValueError:
			print("not floatable")
			return #TODO: nendega midagi
		self.setEnable(False)
		self.instrum.wavelength = newWL
		self.WLreached.clear()

	def setShutter(self, state):
		#sets the shutter state according to self.shutButt if applicable
		pass
