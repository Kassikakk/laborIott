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
		self.dsbl += [self.gotoButt, self.goDeltaButt, self.setSpeedButt, self.xEdit, self.yEdit, self.zEdit, self.speedEdit]
		for i,a in enumerate([self.xEdit, self.yEdit, self.zEdit]):
			if i >= self.dim:
				a.setVisible(False)

		self.mousestep = 0.1  # mm per step
		self.mouseX = True  # mouse direction
		self.posDict = {}

		self.areaLabel.installEventFilter(self)
		self.posList.installEventFilter(self)

		self.setSpeedButt.clicked.connect(self.setSpeed)
		self.gotoButt.clicked.connect(lambda: self.gotoPos([self.xEdit.text(), self.yEdit.text()], False))
		self.goDeltaButt.clicked.connect(lambda: self.gotoPos([self.xEdit.text(), self.yEdit.text()]))
		
		self.centerButt.clicked.connect(self.centerStage)

		self.addListButt.clicked.connect(lambda: self.addToList(self.refEdit.text(), self.stage.pos)) # add position to self.posList (reference from self.refEdit.text()

		self.posList.itemDoubleClicked.connect(self.goByList)
		self.loadButt.clicked.connect(self.loadList)



	def onReconnect(self):
		self.showPos()

	def getPosFields(self):
		postxt = [self.xEdit.text(), self.yEdit.text(),self.zEdit.text()]
		pos = []
		for i in range(self.dim):
			try:
				pos += [float(postxt[i])]
			except ValueError:
				#what now?
				return None
		return pos

	
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
		formtext = ("{:.4f}	" * self.dim)[:-1]
		self.posLabel.setText(formtext.format(*self.instrum.pos))

	def setSpeed(self, newSpeed):
		if not self.posReached.is_set():
			return
		try: 
			newSpeed = float(newSpeed)
		except ValueError:
			print("not floatable")
			return #probably a messagebox should do here
		self.instrum.speed = newSpeed # speed limits are checked within the instrument
		self.speedEdit.setText("{:.1f}".format(self.instrum.speed))

	def gotoPos(self, pos, relative=True):
		if not self.posReached.is_set():
			return
		
		if pos is None: #reset the encoders
			self.instrum.pos = pos
			self.posReached.clear() # to refresh pos
			return
		
		#on the other hand, pos as a list may contain Nones
		try:
			pos = [None if p is None else float(p) for p in pos]
		except ValueError:
			print("not floatable")
			return
		if relative:
			self.instrum.delta = pos
		else:
			self.instrum.pos = pos
		self.posReached.clear()

	def goByList(self, litem):
		#go to pos given by a list item
		#find key from list item
		key = litem.text()
		key = key[:key.find(':')]
		#this assumes there is no ':' in the refname
		#now get the position from dict
		self.gotoPos(self.posDict[key], False)

	def addToList(self, refName, pos):
		# read/generate refname, record position and put them on a list
		nameNotSet = True
		if len(refName) == 0:
			refName = "pos"
		else:
			nameNotSet = refName in self.posDict
		if nameNotSet:
			n = 0
			while(True):
				refName1 = refName + "_%d" % n
				if refName1 in self.posDict:
					n += 1
				else:
					refName = refName1
					break
		self.posDict[refName] = pos
		formtext = ("{}: " + "{:.4f}, "*self.dim)[:-1]
		self.posList.addItem(QtWidgets.QListWidgetItem(formtext.format(refName, *pos)))


		#update listwidget
	def loadList(self):
		fn = QtWidgets.QFileDialog.getOpenFileName(self, 'Open pointlist', self.saveLoc)[0]
		if fn:
			try:
				spc = pd.read_csv(fn, sep = '\t', header = None)
				if spc.shape[1] != self.dim:
					print("Need {} columns.".format(self.dim))
					return
				#we need to make pairs x,y here
				for i in range(len(spc[0])):
					self.addToList('',(spc[0][i],spc[1][i]))
			except:
				print("Hmmm..can't open this")