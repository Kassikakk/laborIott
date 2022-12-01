from threading import Thread
from time import sleep
from PyQt5 import QtCore, QtWidgets
import sys

class testclass(QtCore.QObject):

	sgnl = QtCore.pyqtSignal(int)
	finished = QtCore.pyqtSignal()

	def __init__(self):
		super(testclass, self).__init__()
		self.sgnl.connect(self.outer)
		self.thread = Thread(target=self.thrproc)
		self.finished.connect(lambda: sys.exit())
		self.thread.start()


	def thrproc(self):
		for i in range(10):
			self.sgnl.emit(i)
			sleep(0.5)
			print("Thread: {}".format(i))
		self.finished.emit()

			
	def outer(self,counter):
		print("Outer: {}".format(counter))
		sleep(1)
		


app = QtWidgets.QApplication(sys.argv)
cls = testclass()
sys.exit(app.exec_())
