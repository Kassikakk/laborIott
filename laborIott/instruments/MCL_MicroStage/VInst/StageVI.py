import os, sys
from threading import Event
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.adapters.ZMQAdapter import ZMQAdapter

from laborIott.instruments.MCL_MicroStage.Inst.MicroStage import MCL_MicroStage

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)




class Stage_VI(*uic.loadUiType(localPath('Stage.ui'))):

	def __init__(self, address= None, inport= None, outport = None):
		super(Stage_VI, self).__init__()
		self.setupUi(self)
		self.connectInstr(address, inport, outport)

		self.posReached = Event() #there is currently no threading, so a bool would be ok as well
		self.posReached.set()
		self.dsbl = [self.gotoButt, self.goDeltaButt, self.setSpeedButt, self.xEdit, self.yEdit, self.speedEdit]
		self.external = False
		self.posLabel.setText("{:.4f}	{:.4f}".format(*self.stage.pos))
		self.mousestep = 1.0 #mm per step
		self.mouseX = True #mouse direction

		self.areaLabel.installEventFilter(self)

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.onTimer)
		self.timer.start(200)


	def onTimer(self):
		#handle goingtopos
		if not self.posReached.is_set():
			#check arrival
			self.posLabel.setStyleSheet("color: red")
			if not self.stage.ismoving:
				if not self.external:
					self.setEnable(True)
				self.posReached.set()
				self.posLabel.setStyleSheet("color: black")
				self.posLabel.setText("{:.4f}	{:.4f}".format(*self.stage.pos))


	def connectInstr(self, address, inport, outport):
		#instrumendi tekitamine
		if address is None:
			# local instrument
			#perhaps we could also do the MCL / cryostage selection here
			self.stage = MCL_MicroStage(SDKAdapter(localPath("../Inst/MicroDrive"), False))
		else:
			# connect to remote instrument
			# default port is 5555
			inp = 5555 if inport is None else inport
			outp = inp if outport is None else outport
			self.stage = MCL_MicroStage(ZMQAdapter("MCL_MicroStage", address, inp, outp))

	def move(self, pos, relative = True):
		if not self.posReached.is_set():
			return
		#siin on praegu pooleli.


	def eventFilter(self, o, e):
		if o is self.areaLabel and not self.external:
			if e.type() == QtCore.QEvent.MouseButtonDblClick:
				#the problem is that it still also releases two single clicks
				#so maybe shift + click is better?
				print(e.pos())
				e.accept() #seems to be of no use here
			elif e.type() == QtCore.QEvent.Wheel:
				print(e.angleDelta())
				e.accept()
			elif e.type() == QtCore.QEvent.MouseButtonRelease:
				button = e.button() #1-left 2-right 4-center
				if button == 1:
					if self.mousestep > 0.0002:
						self.mousestep /= 2
				elif button == 2:
					if self.mousestep < 5:
						self.mousestep *= 2
				elif button == 4:
					self.mouseX = not self.mouseX
		return super().eventFilter(o, e)

	def setEnable(self, state):
		for wdg in self.dsbl:
			wdg.setEnabled(state)

	def setExternal(self, state):
		# cancel moving and set enabled/disabled
		self.stage.ismoving = False
		self.posReached.set()
		# set self.acquiring = False
		self.external = state
		# check if not goingtoWL
		self.setEnable(not state)


def StageExitHandler():
	#note howeva that it only works for separate launching, not in multi-instrument procedures
	pass




if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	app.aboutToQuit.connect(StageExitHandler)
	# handle possible command line parameters: address, inport, outport
	args = sys.argv[1:4]
	# port values, if provided, should be integers
	# this errors if they are not
	for i in (1,2):
		if len(args) > i:
			args[i] = int(args[i])

	window = Stage_VI(*args)
	window.show()
	sys.exit(app.exec_())