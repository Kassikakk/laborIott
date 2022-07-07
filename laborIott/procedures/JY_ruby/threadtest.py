#from threading import Thread
from time import sleep
from PyQt5 import QtCore, QtWidgets
import sys

class workclass(QtCore.QThread):

	sgnl = QtCore.pyqtSignal(int)
	finished =  QtCore.pyqtSignal()
	
	def __init__(self):
		super(workclass, self).__init__()
		self.paraator = 54
	
	def run(self):
		for i in range(10):
			self.sgnl.emit(self.paraator) #no nii ta saab küll kätte, aga kuidas suuremate objektidega?
			sleep(0.5)
			print("Thread: {}".format(i))
		self.finished.emit()

class testclass:#(QtCore.QObject):


	def __init__(self):
		super(testclass, self).__init__()
		
	def run(self):
		self.thread = workclass()
		self.thread.started.connect(lambda: print("Ma stardin")) 
		self.thread.finished.connect(self.thread.deleteLater)
		self.thread.finished.connect(lambda: sys.exit())
		self.thread.sgnl.connect(self.outer)
		self.thread.start()
		
			
	def outer(self,counter):
		print("Outer: {}".format(counter))
		sleep(1)
		
		

app = QtWidgets.QApplication(sys.argv)
cls = testclass()
cls.run()
sys.exit(app.exec_())
