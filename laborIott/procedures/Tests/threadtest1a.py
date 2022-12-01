from threading import Thread
from time import sleep
from PyQt5 import QtCore

class signalclass(QtCore.QObject):

	sgnl = QtCore.pyqtSignal(int)

class testclass:


	def __init__(self):
		super(testclass, self).__init__()
		self.thread = Thread(target=self.thrproc)
		self.thread.start()


	def thrproc(self):
		c = signalclass()
		c.sgnl.connect(self.outer)

		for i in range(10):
			c.sgnl.emit(i)
			sleep(0.5)
			print("Thread: {}".format(i))

			
	def outer(self,counter):
		print("Outer: {}".format(counter))
		sleep(1)
		


cls = testclass()
