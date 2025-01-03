import sys, os
from threading import Event
from PyQt5 import QtCore, QtWidgets

from .VInst import VInst


#Niisiis, positsioneerimise VI baasklass
#Oletame, et meil on mingi dimensionaalsus, maei teagi, kuidas seda täpselt tähistada pos[3] või?
#võiks ka USBIO sinna alla ajada phm, kui katik ka kuidagi kampa võtta või siis seda tuletatud klassis ka võib vist

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Position_VI(VInst):

	def __init__(sel,refname, instrument, adapter, dim = 2):
		super().__init__(localPath('Position.ui'),refname, instrument, adapter)
		self.dim = dim #dimensionality
		self.pos = [None]*dim #position
		self.posReached = Event()  
		self.posReached.set()
		self.dsbl += [self.gotoButt, self.goDeltaButt, self.setSpeedButt, self.xEdit, self.yEdit, self.speedEdit]

		self.mousestep = 0.1  # mm per step
		self.mouseX = True  # mouse direction
		self.posDict = {}

		self.areaLabel.installEventFilter(self)
		self.posList.installEventFilter(self)

		self.setSpeedButt.clicked.connect(self.setSpeed)
		self.gotoButt.clicked.connect(lambda: self.gotoPos([self.xEdit.text(), self.yEdit.text()], False))
		self.goDeltaButt.clicked.connect(lambda: self.gotoPos([self.xEdit.text(), self.yEdit.text()]))
		self.resetEncButt.clicked.connect(lambda: self.gotoPos(None))
		self.centerButt.clicked.connect(self.centerStage)

		self.addListButt.clicked.connect(lambda: self.addToList(self.refEdit.text(), self.stage.pos)) # add position to self.posList (reference from self.refEdit.text()

		self.posList.itemDoubleClicked.connect(self.goByList)
		self.loadButt.clicked.connect(self.loadList)



	def onReconnect(self):
		self.showPos()

	
	def onTimer(self):
		super().onTimer()
		# handle goingtopos
		if not self.posReached.is_set():
			# check arrival
			self.posLabel.setStyleSheet("color: red")
			if not self.instrum.ismoving:
				self.posReached.set()
				self.posLabel.setStyleSheet("color: black")
		self.showPos()


	def showPos(self):
		formtext = ["{:.4f}	"] * self.dim
		self.posLabel.setText(formtext.format(*self.instrum.pos))