from threading import Thread
from time import sleep
from PyQt5 import QtCore, QtWidgets
import sys

class workclass(QtCore.QObject):

	sgnl = QtCore.pyqtSignal(int)
	finished =  QtCore.pyqtSignal()
	
	def run(self):
		for i in range(10):
			self.sgnl.emit(i)
			sleep(0.5)
			print("Thread: {}".format(i))
		self.finished.emit()

class testclass(QtCore.QObject):


	def __init__(self):
		super(testclass, self).__init__()
		
	def run(self):
		self.thread = QtCore.QThread()
		self.worker = workclass()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(lambda: print("Ma stardin")) 
		self.thread.started.connect(self.worker.run)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		self.thread.finished.connect(lambda: sys.exit())
		self.worker.sgnl.connect(self.outer)
		print("starting thredas#")
		self.thread.start()
		
			
	def outer(self,counter):
		print("Outer: {}".format(counter))
		sleep(1)
		
		

app = QtWidgets.QApplication(sys.argv)
cls = testclass()
cls.run()
sys.exit(app.exec_())
