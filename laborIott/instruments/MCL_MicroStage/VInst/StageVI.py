import sys
from threading import Event
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from laborIott.adapters.SDKAdapter import SDKAdapter
import pandas as pd

from laborIott.instruments.MCL_MicroStage.Inst.MicroStage import MCL_MicroStage
from laborIott.instruments.VInst import VInst


import os
def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)


class Stage_VI(VInst):

	def __init__(self):
		super().__init__(localPath('Stage.ui'))

		self.stage = MCL_MicroStage(self.getAdapter(SDKAdapter(localPath("../Inst/MicroDrive"), False), "MCL_MS"))

		self.posReached = Event()  
		self.posReached.set()
		self.dsbl += [self.gotoButt, self.goDeltaButt, self.setSpeedButt, self.xEdit, self.yEdit, self.speedEdit]
		self.posLabel.setText("{:.4f}	{:.4f}".format(*self.stage.pos))
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
		'''
		#ja veel ka Delete klahv
		#ja väljast peaks juurde saama numbri ja refi järgi ja võib.olla oleks ka itemite arvu vaja
'''
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)

	def onTimer(self):
		# handle goingtopos
		if not self.posReached.is_set():
			# check arrival
			self.posLabel.setStyleSheet("color: red")
			if not self.stage.ismoving:
				#if not self.external:
				#	self.setEnable(True)
				self.posReached.set()
				self.posLabel.setStyleSheet("color: black")
				self.posLabel.setText("{:.4f}	{:.4f}".format(*self.stage.pos))


	def setSpeed(self, newSpeed):
		if not self.posReached.is_set():
			return
		try: 
			newSpeed = float(newSpeed)
		except ValueError:
			print("not floatable")
			return #probably a messagebox should do here
		self.stage.speed = newSpeed # speed limits are checked within the instrument
		self.speedEdit.setText("{:.1f}".format(self.stage.speed))

	def gotoPos(self, pos, relative=True):
		if not self.posReached.is_set():
			return
		
		if pos is None: #reset the encoders
			self.stage.pos = pos
			self.posReached.clear() # to refresh pos
			return
		
		#on the other hand, pos as a list may contain Nones
		try:
			pos = [None if p is None else float(p) for p in pos]
		except ValueError:
			print("not floatable")
			return
		if relative:
			self.stage.delta = pos
		else:
			self.stage.pos = pos
		self.posReached.clear()


	def goByList(self, litem):
		#go to pos given by a list item
		#find key from list item
		key = litem.text()
		key = key[:key.find(':')]
		#this assumes there is no ':' in the refname
		#now get the position from dict
		self.gotoPos(self.posDict[key], False)
	
	def centerStage(self):
		#move stage to extremes
		poss = []
		for p in [[-100,0],[0,-100],[100,0], [0,100]]:
			self.stage.pos = p
			while self.stage.ismoving:
				pass
			poss += [self.stage.pos]
		self.stage.pos = [(poss[0][0] + poss[2][0])/2,(poss[1][1] + poss[3][1])/2]
		self.posReached.clear()

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
				if self.mouseX:
					self.gotoPos((step, None))
				else:
					self.gotoPos((None, step))

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
					self.mouseX = not self.mouseX
				#set the label here
				self.mouseMoveLabel.setText("Dir: %s Step: %.4f" % ('X' if self.mouseX else 'Y', self.mousestep))
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
		self.posList.addItem(QtWidgets.QListWidgetItem("%s: (%.4f, %.4f)" % (refName, pos[0], pos[1])))


		#update listwidget
	def loadList(self):
		fn = QtWidgets.QFileDialog.getOpenFileName(self, 'Open pointlist', self.saveLoc)[0]
		if fn:
			try:
				spc = pd.read_csv(fn, sep = '\t', header = None)
				if spc.shape[1] != 2:
					print("Need two columns.")
					return
				#we need to make pairs x,y here
				for i in range(len(spc[0])):
					self.addToList('',(spc[0][i],spc[1][i]))
			except:
				print("Hmmm..can't open this")

	def saveData(self, name): #override
		#prepare xdata and ydata
		self.xdata = []
		self.ydata = []
		for k in self.posDict:
			self.xdata += [self.posDict[k][0]]
			self.ydata += [self.posDict[k][1]]
		super().saveData(name)





	def setExternal(self, state):
		# cancel moving and set enabled/disabled
		self.stage.ismoving = False
		self.posReached.set()
		super().setExternal(state)





if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	
	window = Stage_VI()
	window.show()
	sys.exit(app.exec_())
