import sys, os
from threading import Event
from PyQt5 import QtCore, QtWidgets
import pandas as pd

from .VInst import VInst


#Niisiis, positsioneerimise VI baasklass
#Oletame, et meil on mingi dimensionaalsus, maei teagi, kuidas seda täpselt tähistada pos[3] või?
#võiks ka USBIO sinna alla ajada phm, kui katik ka kuidagi kampa võtta või siis seda tuletatud klassis ka võib vist

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Position_VI(VInst):

	def __init__(self,refname, instrument, adapter, dim = 2):
		super().__init__(localPath('Position.ui'),refname, instrument, adapter)
		self.dim = dim #dimensionality
		self.pos = [None]*dim #position
		self.sigref = [None,None] #signal and reference positions used in some scenarios
		self.posReached = Event()  
		self.posReached.set()
		self.dsbl += [self.gotoButt, self.goDeltaButt, self.setSpeedButt, self.xEdit, self.yEdit, self.zEdit, self.speedEdit]
		for i,a in enumerate([self.xEdit, self.yEdit, self.zEdit]):
			if i >= self.dim:
				a.setVisible(False)

		self.mousestep = 0.1  # mm per step
		self.mousedim = 0  # mouse direction
		self.posDict = {}

		self.mouseMoveLabel.setText("Dir: {} Step: {:.4f}".format('XYZ'[self.mousedim], self.mousestep))

		self.areaLabel.installEventFilter(self)
		self.posList.installEventFilter(self)

		self.setSpeedButt.clicked.connect(self.setSpeed)
		self.gotoButt.clicked.connect(lambda: self.gotoPos([self.xEdit.text(), self.yEdit.text()], False))
		self.goDeltaButt.clicked.connect(lambda: self.gotoPos([self.xEdit.text(), self.yEdit.text()]))
		
		self.centerButt.clicked.connect(self.centerStage)

		self.addListButt.clicked.connect(lambda: self.addToList(self.refEdit.text(), self.instrum.pos)) # add position to self.posList (reference from self.refEdit.text()

		self.posList.itemDoubleClicked.connect(self.goByList)
		self.loadButt.clicked.connect(self.loadList)



	def onReconnect(self):
		super().onReconnect()
		print("reconn")

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
		#make sure there is no : in the refname
		refName = refName.replace(':','_')
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
		#use the special names sig and ref for the signal and reference positions
		if refName == "sig":
			self.sigref[0] = pos
		elif refName == "ref":
			self.sigref[1] = pos

		formtext = ("{}: " + "{:.4f}, "*self.dim)[:-2]
		self.posList.addItem(QtWidgets.QListWidgetItem(formtext.format(refName, *pos)))


		#update listwidget
	def loadList(self):
		#TODO: This isn't working correctly (dimension support!) and the save part needs to be overridden too
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

	def eventFilter(self, o, e):
		if self.external:
			return super().eventFilter(o, e)
		if o is self.areaLabel:
			if e.type() == QtCore.QEvent.MouseButtonDblClick:
				# the problem is that it still also releases two single clicks
				# so maybe shift + click is better?
				#print(e.pos())
				e.accept()  # seems to be of no use here
			elif e.type() == QtCore.QEvent.Wheel:
				step = self.mousestep if e.angleDelta().y() > 0 else -self.mousestep # angleDelta needs some adjustment here
				toPos = []
				for i in range(self.dim):
					toPos += [step] if i == self.mousedim else [None]
				self.gotoPos(toPos)

			elif e.type() == QtCore.QEvent.MouseButtonRelease:
				button = e.button()  # 1-left 2-right 4-center
				if button == 1:
					#maybe if modifier = Ctrl, goto point?
					if self.mousestep > 0.0002:
						self.mousestep /= 2
				elif button == 2:
					if self.mousestep < 5:
						self.mousestep *= 2
				elif button == 4:
					self.mousedim += 1
					if self.mousedim >= self.dim:
						self.mousedim = 0
				#set the label here
				self.mouseMoveLabel.setText("Dir: {} Step: {:.4f}".format('XYZ'[self.mousedim], self.mousestep))
		elif o is self.posList:
			if (e.type() == QtCore.QEvent.KeyPress) and (e.key() == QtCore.Qt.Key_Delete):
				#if modifier, delete all, else del current
				if e.modifiers() == QtCore.Qt.ControlModifier:
					#get all items into a list
					listItems = self.posList.findItems("*", QtCore.Qt.MatchWildcard)
				else:
					#selected items
					listItems = self.posList.selectedItems()
				for item in listItems:
					key = item.text()
					key = key[:key.find(':')]
					self.posDict.pop(key)
					self.posList.takeItem(self.posList.row(item))
		return super().eventFilter(o, e)